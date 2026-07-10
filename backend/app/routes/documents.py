from datetime import datetime, timezone

from flask import g, request, send_file
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..middleware import auth_required, roles_required
from ..models.estudiante import Estudiante
from ..models.plan_estudio import PlanEstudio
from ..models.solicitud_documento import SolicitudDocumento
from ..schemas.document_schema import (
    DocumentoAutorizar,
    DocumentoVerificacionResponse,
    QrVerificacionPath,
    SolicitudDocumentoPath,
    SolicitudDocumentoResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.document_service import DocumentService
from ..services.file_service import FileService
from ..services.tipo_documento_service import TipoDocumentoService

documents_tag = Tag(
    name="Certificados y Documentos",
    description="Solicitud, autorizacion y emision de documentos oficiales",
)

documents_bp = APIBlueprint("documents", __name__, abp_tags=[documents_tag])


def _comprobante_public_url(solicitud):
    if not solicitud.comprobante_url:
        return None
    if solicitud.comprobante_url.startswith("http") or solicitud.comprobante_url.startswith("/api/"):
        return solicitud.comprobante_url
    return f"/api/documentos/solicitudes/{solicitud.id}/comprobante"


def _serialize_solicitud(solicitud):
    return SolicitudDocumentoResponse(
        id=solicitud.id,
        estudiante_id=solicitud.estudiante_id,
        tipo_documento_id=solicitud.tipo_documento_id,
        tipo_documento=solicitud.tipo_documento,
        estado=solicitud.estado,
        qr_hash=solicitud.qr_hash,
        archivo_url=solicitud.archivo_url,
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
            .joinedload(PlanEstudio.especialidad),
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
    responses={"200": {"description": "Listado de solicitudes"}, "401": ErrorResponse},
)
@auth_required
def list_document_requests():
    """Listar solicitudes de documentos segun el rol autenticado."""
    user = g.current_user

    query = SolicitudDocumento.query
    if user.rol == "estudiante":
        if not user.estudiante:
            return {"error": "El usuario no tiene perfil de estudiante"}, 400
        query = query.filter_by(estudiante_id=user.estudiante.id)

    solicitudes = query.order_by(SolicitudDocumento.id.desc()).all()
    return {"data": [_serialize_solicitud(solicitud) for solicitud in solicitudes]}, 200


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
            # Compatibilidad: nombre libre fuera del catálogo (sin pago)
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

    solicitud = SolicitudDocumento(
        estudiante_id=user.estudiante.id,
        tipo_documento_id=tipo_documento_id,
        tipo_documento=tipo_nombre_final,
        estado="pendiente_autorizacion",
        requiere_pago=requiere_pago,
        fecha_creacion=datetime.now(timezone.utc),
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

    solicitud.estado = "autorizado" if body.aprobado else "rechazado"
    db.session.commit()

    return _serialize_solicitud(solicitud), 200


@documents_bp.post(
    "/solicitudes/<int:solicitud_id>/emitir",
    responses={"200": SolicitudDocumentoResponse, "403": ErrorResponse, "404": ErrorResponse},
)
@roles_required("administrador")
def issue_document(path: SolicitudDocumentoPath):
    """Emitir certificados con PDF y codigo QR generados automaticamente."""
    solicitud = _get_solicitud_with_relations(path.solicitud_id)
    if not solicitud:
        return {"error": "Solicitud no encontrada"}, 404

    if solicitud.estado != "autorizado":
        return {"error": "La solicitud debe estar autorizada antes de emitirse"}, 400

    try:
        archivo_url, qr_hash = DocumentService.generate_document(solicitud)
    except Exception:
        return {"error": "No se pudo generar el documento PDF"}, 500

    solicitud.estado = "emitido"
    solicitud.archivo_url = archivo_url
    solicitud.qr_hash = qr_hash
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

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{solicitud.tipo_documento.replace(' ', '_')}-{solicitud.id}.pdf",
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
        return (
            DocumentoVerificacionResponse(
                valido=False,
                mensaje="Documento no encontrado o codigo invalido",
            ).model_dump(),
            404,
        )

    estudiante = solicitud.estudiante.user
    return (
        DocumentoVerificacionResponse(
            valido=True,
            solicitud_id=solicitud.id,
            tipo_documento=solicitud.tipo_documento,
            estudiante=f"{estudiante.nombres} {estudiante.apellidos}",
            estado=solicitud.estado,
            fecha_emision=solicitud.fecha_creacion,
            mensaje="Documento valido y emitido por el sistema",
        ).model_dump(),
        200,
    )
