from datetime import datetime, timezone

from flask import g
from flask_openapi3 import APIBlueprint, Tag

from ..extensions import db
from ..middleware import auth_required, roles_required
from ..models.solicitud_documento import SolicitudDocumento
from ..schemas.document_schema import (
    DocumentoAutorizar,
    DocumentoEmitir,
    SolicitudDocumentoCreate,
    SolicitudDocumentoPath,
    SolicitudDocumentoResponse,
)
from ..schemas.generic_schema import ErrorResponse

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
def issue_document(path: SolicitudDocumentoPath, body: DocumentoEmitir):
    """Emitir certificados con firma digital o codigo QR."""
    solicitud = SolicitudDocumento.query.get(path.solicitud_id)
    if not solicitud:
        return {"error": "Solicitud no encontrada"}, 404

    if solicitud.estado != "autorizado":
        return {"error": "La solicitud debe estar autorizada antes de emitirse"}, 400

    solicitud.estado = "emitido"
    solicitud.archivo_url = body.archivo_url
    solicitud.qr_hash = body.qr_hash
    db.session.commit()

    return _serialize_solicitud(solicitud), 200
