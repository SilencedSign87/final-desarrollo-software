from flask_openapi3 import APIBlueprint, Tag

from ..schemas.tipo_documento_schema import (
    TipoDocumentoCreate,
    TipoDocumentoListResponse,
    TipoDocumentoPath,
    TipoDocumentoResponse,
    TipoDocumentoUpdate,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.tipo_documento_service import TipoDocumentoService
from ..services.auth_service import AuthService

tipo_documento_tag = Tag(
    name="Tipo de Documento",
    description="Catálogo de documentos y configuración de pago",
)

tipo_documento_bp = APIBlueprint(
    "tipo_documento", __name__, abp_tags=[tipo_documento_tag]
)


def _to_response(tipo):
    return TipoDocumentoResponse(
        id=tipo.id,
        nombre=tipo.nombre,
        requiere_pago=tipo.requiere_pago,
        activo=tipo.activo,
    ).model_dump()


@tipo_documento_bp.get(
    "/",
    responses={"200": TipoDocumentoListResponse},
)
def listar_tipos():
    """Listar tipos de documento. Estudiantes solo ven activos."""
    user = AuthService.get_current_user()
    solo_activos = not user or user.rol == "estudiante"
    tipos = TipoDocumentoService.listar(solo_activos=solo_activos)
    return [_to_response(t) for t in tipos], 200


@tipo_documento_bp.post(
    "/",
    responses={"201": TipoDocumentoResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def crear_tipo(body: TipoDocumentoCreate):
    """Admin o dirección crea un tipo de documento."""
    user = AuthService.get_current_user()
    if not user or user.rol not in ("administrador", "direccion"):
        return {"error": "No autorizado"}, 401

    try:
        tipo = TipoDocumentoService.crear(body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    return _to_response(tipo), 201


@tipo_documento_bp.put(
    "/<int:tipo_id>",
    responses={"200": TipoDocumentoResponse, "400": ErrorResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def actualizar_tipo(path: TipoDocumentoPath, body: TipoDocumentoUpdate):
    """Admin o dirección actualiza un tipo (incluye requiere_pago)."""
    user = AuthService.get_current_user()
    if not user or user.rol not in ("administrador", "direccion"):
        return {"error": "No autorizado"}, 401

    try:
        tipo = TipoDocumentoService.actualizar(
            path.tipo_id, body.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        return {"error": str(e)}, 400

    if not tipo:
        return {"error": "Tipo de documento no encontrado"}, 404

    return _to_response(tipo), 200


@tipo_documento_bp.delete(
    "/<int:tipo_id>",
    responses={"200": {"description": "Eliminado"}, "401": ErrorResponse, "404": ErrorResponse},
)
def eliminar_tipo(path: TipoDocumentoPath):
    """Admin o dirección elimina un tipo de documento."""
    user = AuthService.get_current_user()
    if not user or user.rol not in ("administrador", "direccion"):
        return {"error": "No autorizado"}, 401

    eliminado = TipoDocumentoService.eliminar(path.tipo_id)
    if not eliminado:
        return {"error": "Tipo de documento no encontrado"}, 404

    return {"message": "Tipo de documento eliminado"}, 200
