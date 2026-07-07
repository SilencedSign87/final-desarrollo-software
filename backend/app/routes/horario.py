from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from ..schemas.horario_schema import (
    HorarioCreate,
    HorarioUpdate,
    HorarioResponse,
    HorarioListResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.horario_service import HorarioService
from ..services.auth_service import AuthService

horario_tag = Tag(name="Horario", description="Gestión de horarios de secciones")

horario_bp = APIBlueprint("horario", __name__, abp_tags=[horario_tag])


class HorarioPath(BaseModel):
    horario_id: int = Field(..., description="ID del horario")


class HorarioQuery(BaseModel):
    seccion_id: int | None = Field(None)


def _to_response(horario):
    return HorarioResponse(
        id=horario.id,
        seccion_id=horario.seccion_id,
        dia_semana=horario.dia_semana,
        hora_inicio=horario.hora_inicio,
        hora_final=horario.hora_final,
        aula=horario.aula,
    ).model_dump(mode="json")


@horario_bp.post(
    "/",
    responses={"201": HorarioResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def crear_horario(body: HorarioCreate):
    """Admin crea un horario para una sección"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede crear horarios"}, 401

    try:
        horario = HorarioService.crear_horario(body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    return _to_response(horario), 201


@horario_bp.get(
    "/",
    responses={"200": HorarioListResponse},
)
def listar_horarios(query: HorarioQuery):
    """Listar horarios (filtrable por sección)"""
    horarios = HorarioService.listar_horarios(query.seccion_id)
    return [_to_response(h) for h in horarios], 200


@horario_bp.get(
    "/<int:horario_id>",
    responses={"200": HorarioResponse, "404": ErrorResponse},
)
def obtener_horario(path: HorarioPath):
    """Detalle de un horario"""
    horario = HorarioService.obtener_horario(path.horario_id)
    if not horario:
        return {"error": "Horario no encontrado"}, 404
    return _to_response(horario), 200


@horario_bp.put(
    "/<int:horario_id>",
    responses={"200": HorarioResponse, "400": ErrorResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def actualizar_horario(path: HorarioPath, body: HorarioUpdate):
    """Admin edita un horario existente"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede editar horarios"}, 401

    try:
        horario = HorarioService.actualizar_horario(path.horario_id, body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    if not horario:
        return {"error": "Horario no encontrado"}, 404
    return _to_response(horario), 200


@horario_bp.delete(
    "/<int:horario_id>",
    responses={"200": {"description": "Horario eliminado"}, "401": ErrorResponse, "404": ErrorResponse},
)
def eliminar_horario(path: HorarioPath):
    """Admin elimina un horario"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede eliminar horarios"}, 401

    eliminado = HorarioService.eliminar_horario(path.horario_id)
    if not eliminado:
        return {"error": "Horario no encontrado"}, 404
    return {"message": "Horario eliminado correctamente"}, 200