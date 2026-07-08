from datetime import datetime, timezone

from flask import g, send_file
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
    SolicitudDocumentoCreate,
    SolicitudDocumentoPath,
    SolicitudDocumentoResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.document_service import DocumentService

documents_tag = Tag(
    name="Certificados y Documentos",
    description="Solicitud, autorizacion y emision de documentos oficiales",
)

documents_bp = APIBlueprint("documents", __name__, abp_tags=[documents_tag])


def _serialize_solicitud(solicitud):
    return SolicitudDocumentoResponse(
        id=solicitud.id,
        estudiante_id=solicitud.estudiante_id,
        tipo_documento=solicitud.tipo_documento,
        estado=solicitud.estado,
        qr_hash=solicitud.qr_hash,
        archivo_url=solicitud.archivo_url,
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
def create_document_request(body: SolicitudDocumentoCreate):
    """Solicitar un certificado o constancia en linea."""
    user = g.current_user
    if not user.estudiante:
        return {"error": "El usuario no tiene perfil de estudiante"}, 400

    solicitud = SolicitudDocumento(
        estudiante_id=user.estudiante.id,
        tipo_documento=body.tipo_documento,
        estado="pendiente_autorizacion",
        fecha_creacion=datetime.now(timezone.utc),
    )
    db.session.add(solicitud)
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
