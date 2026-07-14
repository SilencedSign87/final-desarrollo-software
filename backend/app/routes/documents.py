from datetime import datetime, timezone

from flask import g, render_template, request, send_file
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..middleware import auth_required, roles_required
from ..models.estudiante import Estudiante
from ..models.especialidad import Especialidad
from ..models.plan_estudio import PlanEstudio
from ..models.solicitud_documento import SolicitudDocumento
from ..schemas.document_schema import (
    DocumentoAutorizar,
    DocumentoVerificacionResponse,
    PaginationMeta,
    QrVerificacionPath,
    SolicitudDocumentoPath,
    SolicitudDocumentoQuery,
    SolicitudDocumentoResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.document_service import DocumentService
from ..services.file_service import FileService
from ..services.signature_service import SignatureService
from ..services.tipo_documento_service import TipoDocumentoService
from ..services.audit_service import AuditService
from ..utils.datetime_utils import format_lima


def _wants_html() -> bool:
    """Los navegadores (escaneo de QR) piden HTML; la API puede pedir JSON."""
    accept = request.headers.get("Accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return False
    if request.args.get("format") == "json":
        return False
    return "text/html" in accept or request.args.get("format") == "html" or not accept


documents_tag = Tag(
    name="Certificados y Documentos",
    description="Solicitud, autorizacion y emision de documentos oficiales",
)

documents_bp = APIBlueprint("documents", __name__, abp_tags=[documents_tag])


def _comprobante_public_url(solicitud):
    """Ruta relativa para que el frontend la resuelva con VITE_API_URL."""
    if not solicitud.comprobante_url:
        return None
    stored = solicitud.comprobante_url
    if stored.startswith("http") and "/api/documentos/" not in stored:
        return stored
    return f"/api/documentos/solicitudes/{solicitud.id}/comprobante"


def _archivo_public_url(solicitud):
    """Ruta relativa; ignora hosts localhost guardados al emitir."""
    if not solicitud.archivo_url:
        return None
    stored = solicitud.archivo_url
    if stored.startswith("http") and "/api/documentos/" not in stored:
        return stored
    return f"/api/documentos/solicitudes/{solicitud.id}/archivo"


def _serialize_solicitud(solicitud):
    return SolicitudDocumentoResponse(
        id=solicitud.id,
        codigo_ticket=solicitud.codigo_ticket,
        estudiante_id=solicitud.estudiante_id,
        tipo_documento_id=solicitud.tipo_documento_id,
        tipo_documento=solicitud.tipo_documento,
        estado=solicitud.estado,
        observacion=solicitud.observacion,
        qr_hash=solicitud.qr_hash,
        firma_digital=solicitud.firma_digital,
        archivo_url=_archivo_public_url(solicitud),
        comprobante_url=_comprobante_public_url(solicitud),
        requiere_pago=bool(solicitud.requiere_pago),
        fecha_creacion=solicitud.fecha_creacion,
    ).model_dump()


def _get_solicitud_with_relations(solicitud_id: int):
    return (
        SolicitudDocumento.query.options(
            joinedload(SolicitudDocumento.estudiante).joinedload(Estudiante.user),
            joinedload(SolicitudDocumento.estudiante)
            .joinedload(Estudiante.plan_estudio)
            .joinedload(PlanEstudio.especialidad)
            .joinedload(Especialidad.facultad),
        )
        .filter_by(id=solicitud_id)
        .first()
    )


def _can_access_document(user, solicitud) -> bool:
    if user.rol in {"administrador", "direccion", "docente"}:
        return True
    if user.rol == "estudiante" and user.estudiante:
        return solicitud.estudiante_id == user.estudiante.id
    return False


@documents_bp.get(
    "/solicitudes",
    responses={"200": {"description": "Listado paginado de solicitudes"}, "401": ErrorResponse},
)
@auth_required
def list_document_requests(query: SolicitudDocumentoQuery):
    """Listar solicitudes de documentos con filtros y paginación."""
    user = g.current_user

    base_query = SolicitudDocumento.query
    if user.rol == "estudiante":
        if not user.estudiante:
            return {"error": "El usuario no tiene perfil de estudiante"}, 400
        base_query = base_query.filter_by(estudiante_id=user.estudiante.id)

    if query.estado:
        base_query = base_query.filter_by(estado=query.estado)

    pagination = base_query.order_by(SolicitudDocumento.id.desc()).paginate(
        page=query.page,
        per_page=query.per_page,
        error_out=False,
    )

    return {
        "data": [_serialize_solicitud(solicitud) for solicitud in pagination.items],
        "meta": PaginationMeta(
            page=pagination.page,
            per_page=pagination.per_page,
            total=pagination.total,
            pages=pagination.pages,
        ).model_dump(),
    }, 200


@documents_bp.post(
    "/solicitudes",
    responses={"201": SolicitudDocumentoResponse, "400": ErrorResponse, "401": ErrorResponse},
)
@roles_required("estudiante")
def create_document_request():
    """Solicitar un certificado o constancia (JSON o multipart con comprobante)."""
    user = g.current_user
    if not user.estudiante:
        return {"error": "El usuario no tiene perfil de estudiante"}, 400

    comprobante_file = None
    tipo_documento_id = None
    tipo_nombre = None

    if request.content_type and "multipart/form-data" in request.content_type:
        raw_id = request.form.get("tipo_documento_id")
        tipo_nombre = request.form.get("tipo_documento")
        if raw_id:
            try:
                tipo_documento_id = int(raw_id)
            except ValueError:
                return {"error": "tipo_documento_id inválido"}, 400
        comprobante_file = request.files.get("comprobante")
    else:
        body = request.get_json(silent=True) or {}
        tipo_documento_id = body.get("tipo_documento_id")
        tipo_nombre = body.get("tipo_documento")

    tipo = None
    if tipo_documento_id:
        tipo = TipoDocumentoService.obtener(tipo_documento_id)
        if not tipo or not tipo.activo:
            return {"error": "Tipo de documento no encontrado o inactivo"}, 400
    elif tipo_nombre:
        tipo = TipoDocumentoService.obtener_por_nombre(tipo_nombre)
        if not tipo:
            tipo_nombre_final = tipo_nombre
            requiere_pago = False
            tipo_documento_id = None
        else:
            tipo_nombre_final = tipo.nombre
            requiere_pago = tipo.requiere_pago
            tipo_documento_id = tipo.id
    else:
        return {"error": "Debes indicar el tipo de documento"}, 400

    if tipo is not None:
        tipo_nombre_final = tipo.nombre
        requiere_pago = tipo.requiere_pago
        tipo_documento_id = tipo.id

    tiene_archivo = comprobante_file is not None and getattr(
        comprobante_file, "filename", None
    )

    if requiere_pago and not tiene_archivo:
        return {
            "error": "Este documento requiere comprobante de pago. Adjunta el archivo."
        }, 400

    if tiene_archivo:
        try:
            FileService.validate_comprobante(comprobante_file)
        except ValueError as e:
            return {"error": str(e)}, 400

    fecha_creacion = datetime.now(timezone.utc)
    solicitud = SolicitudDocumento(
        estudiante_id=user.estudiante.id,
        tipo_documento_id=tipo_documento_id,
        tipo_documento=tipo_nombre_final,
        codigo_ticket=DocumentService.generate_ticket_code(fecha_creacion),
        estado="pendiente_autorizacion",
        requiere_pago=requiere_pago,
        fecha_creacion=fecha_creacion,
    )
    db.session.add(solicitud)
    db.session.flush()

    if tiene_archivo:
        stored = FileService.save_comprobante(
            comprobante_file, f"documento-{solicitud.id}"
        )
        solicitud.comprobante_url = stored

    db.session.commit()

    return _serialize_solicitud(solicitud), 201


@documents_bp.post(
    "/solicitudes/<int:solicitud_id>/autorizar",
    responses={"200": SolicitudDocumentoResponse, "403": ErrorResponse, "404": ErrorResponse},
)
@roles_required("direccion")
def authorize_document_request(path: SolicitudDocumentoPath, body: DocumentoAutorizar):
    """Autorizar o rechazar la emision de documentos oficiales."""
    solicitud = SolicitudDocumento.query.get(path.solicitud_id)
    if not solicitud:
        return {"error": "Solicitud no encontrada"}, 404

    if solicitud.estado != "pendiente_autorizacion":
        return {"error": "Solo se pueden revisar solicitudes pendientes de autorización"}, 400

    if body.aprobado:
        solicitud.estado = "autorizado"
        solicitud.observacion = body.observacion.strip() if body.observacion else None
        AuditService.log(
            accion="autorizar_documento",
            recurso=solicitud.codigo_ticket or f"solicitud:{solicitud.id}",
            detalle=f"Documento autorizado: {solicitud.tipo_documento}",
            user=g.current_user,
        )
    else:
        solicitud.estado = "rechazado"
        solicitud.observacion = body.observacion.strip()
        AuditService.log(
            accion="rechazar_documento",
            recurso=solicitud.codigo_ticket or f"solicitud:{solicitud.id}",
            detalle=f"Documento rechazado: {solicitud.observacion}",
            user=g.current_user,
        )

    solicitud.respondido_por_user_id = g.current_user.id
    solicitud.fecha_respuesta = datetime.now(timezone.utc)
    db.session.commit()

    return _serialize_solicitud(solicitud), 200


@documents_bp.post(
    "/solicitudes/<int:solicitud_id>/emitir",
    responses={"200": SolicitudDocumentoResponse, "403": ErrorResponse, "404": ErrorResponse},
)
@roles_required("administrador")
def issue_document(path: SolicitudDocumentoPath):
    """Emitir certificados con PDF, firma digital y codigo QR."""
    solicitud = _get_solicitud_with_relations(path.solicitud_id)
    if not solicitud:
        return {"error": "Solicitud no encontrada"}, 404

    if solicitud.estado != "autorizado":
        return {"error": "La solicitud debe estar autorizada antes de emitirse"}, 400

    try:
        archivo_url, qr_hash, firma_info = DocumentService.generate_document(solicitud)
    except Exception:
        return {"error": "No se pudo generar el documento PDF"}, 500

    solicitud.estado = "emitido"
    solicitud.archivo_url = archivo_url
    solicitud.qr_hash = qr_hash
    solicitud.firma_digital = firma_info["firma_digital"]
    solicitud.firma_algoritmo = firma_info["firma_algoritmo"]
    solicitud.firma_huella_cert = firma_info["firma_huella_cert"]
    solicitud.contenido_hash = firma_info["contenido_hash"]
    solicitud.fecha_emision = datetime.now(timezone.utc)
    AuditService.log(
        accion="emitir_documento",
        recurso=solicitud.codigo_ticket or f"solicitud:{solicitud.id}",
        detalle=f"Documento emitido con firma digital: {solicitud.tipo_documento}",
        user=g.current_user,
    )
    db.session.commit()

    return _serialize_solicitud(solicitud), 200


@documents_bp.get(
    "/solicitudes/<int:solicitud_id>/archivo",
    responses={"200": {"description": "Archivo PDF del documento"}, "403": ErrorResponse, "404": ErrorResponse},
)
@auth_required
def download_document_file(path: SolicitudDocumentoPath):
    """Descargar el PDF emitido de una solicitud."""
    solicitud = SolicitudDocumento.query.get(path.solicitud_id)
    if not solicitud:
        return {"error": "Solicitud no encontrada"}, 404

    if solicitud.estado != "emitido":
        return {"error": "El documento aun no ha sido emitido"}, 400

    user = g.current_user
    if not _can_access_document(user, solicitud):
        return {"error": "No tienes permisos para acceder a este documento"}, 403

    pdf_path = DocumentService.get_pdf_path(solicitud.id)
    if not pdf_path:
        return {"error": "Archivo no encontrado"}, 404

    ticket = solicitud.codigo_ticket or str(solicitud.id)
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{solicitud.tipo_documento.replace(' ', '_')}-{ticket}.pdf",
    )


@documents_bp.get(
    "/solicitudes/<int:solicitud_id>/comprobante",
    responses={
        "200": {"description": "Comprobante de pago de la solicitud"},
        "403": ErrorResponse,
        "404": ErrorResponse,
    },
)
@auth_required
def download_document_comprobante(path: SolicitudDocumentoPath):
    """Descargar el comprobante de pago adjunto a la solicitud."""
    solicitud = SolicitudDocumento.query.get(path.solicitud_id)
    if not solicitud:
        return {"error": "Solicitud no encontrada"}, 404

    user = g.current_user
    if not _can_access_document(user, solicitud):
        return {"error": "No tienes permisos para acceder a este comprobante"}, 403

    if not solicitud.comprobante_url:
        return {"error": "Esta solicitud no tiene comprobante"}, 404

    path_file = FileService.get_comprobante_path(solicitud.comprobante_url)
    if not path_file:
        return {"error": "Archivo de comprobante no encontrado"}, 404

    return send_file(
        path_file,
        mimetype=FileService.mimetype_for(path_file.name),
        as_attachment=True,
        download_name=path_file.name,
    )


@documents_bp.get(
    "/verificar/<string:qr_hash>",
    responses={"200": DocumentoVerificacionResponse, "404": ErrorResponse},
)
def verify_document(path: QrVerificacionPath):
    """Verificar la autenticidad de un documento emitido mediante su codigo QR."""
    solicitud = (
        SolicitudDocumento.query.options(
            joinedload(SolicitudDocumento.estudiante).joinedload(Estudiante.user),
        )
        .filter_by(qr_hash=path.qr_hash, estado="emitido")
        .first()
    )

    if not solicitud:
        payload = DocumentoVerificacionResponse(
            valido=False,
            mensaje="No encontramos un documento emitido con este código QR.",
        ).model_dump()
        if _wants_html():
            return (
                render_template(
                    "document_verification.html",
                    qr_hash=path.qr_hash,
                    **payload,
                ),
                404,
            )
        return payload, 404

    firma_valida = SignatureService.verify_signature(
        solicitud,
        solicitud.qr_hash,
        solicitud.firma_digital,
    )
    estudiante = solicitud.estudiante.user
    fecha = solicitud.fecha_emision or solicitud.fecha_creacion
    payload = DocumentoVerificacionResponse(
        valido=True,
        solicitud_id=solicitud.id,
        codigo_ticket=solicitud.codigo_ticket,
        tipo_documento=solicitud.tipo_documento,
        estudiante=f"{estudiante.nombres} {estudiante.apellidos}",
        estado=solicitud.estado,
        fecha_emision=fecha,
        firma_valida=firma_valida,
        mensaje=(
            "Documento válido y emitido por el sistema académico."
            if firma_valida
            else "El documento existe, pero la firma digital no es válida."
        ),
    ).model_dump()

    if _wants_html():
        return render_template(
            "document_verification.html",
            qr_hash=path.qr_hash,
            valido=payload["valido"],
            mensaje=payload["mensaje"],
            tipo_documento=payload["tipo_documento"],
            estudiante=payload["estudiante"],
            codigo_ticket=payload["codigo_ticket"],
            estado=payload["estado"],
            fecha_emision=format_lima(fecha) if fecha else "—",
            firma_valida=payload["firma_valida"],
        )

    return payload, 200
