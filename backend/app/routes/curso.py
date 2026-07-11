from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from ..schemas.curso_schema import (
    CursoCreate,
    CursoUpdate,
    CursoResponse,
    CursoListResponse,
    CursosDisponiblesResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.curso_service import CursoService
from ..services.auth_service import AuthService
from ..services.matricula_service import MatriculaService

curso_tag = Tag(name="Curso", description="Gestión de cursos del plan de estudios")

curso_bp = APIBlueprint("curso", __name__, abp_tags=[curso_tag])


class CursoPath(BaseModel):
    curso_id: int = Field(..., description="ID del curso")


class CursoQuery(BaseModel):
    plan_estudios_id: int | None = Field(None)
    semestre_num: int | None = Field(None)


def _to_response(curso):
    return CursoResponse(
        id=curso.id,
        plan_estudios_id=curso.plan_estudios_id,
        nombre=curso.nombre,
        horas_teoria=curso.horas_teoria,
        horas_practica=curso.horas_practica,
        semestre_num=curso.semestre_num,
        prerequisitos_ids=[p.id for p in curso.prerequisitos],
    ).model_dump()


@curso_bp.post(
    "/",
    responses={"201": CursoResponse, "401": ErrorResponse},
)
def crear_curso(body: CursoCreate):
    """Admin crea un nuevo curso"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede crear cursos"}, 401

    curso = CursoService.crear_curso(body.model_dump())
    return _to_response(curso), 201


@curso_bp.get(
    "/",
    responses={"200": CursoListResponse},
)
def listar_cursos(query: CursoQuery):
    """Listar cursos (filtrable por plan de estudios o semestre). Público para cualquier autenticado."""
    cursos = CursoService.listar_cursos(query.plan_estudios_id, query.semestre_num)
    return [_to_response(c) for c in cursos], 200


@curso_bp.get(
    "/disponibles",
    responses={"200": CursosDisponiblesResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def listar_disponibles():
    """El estudiante autenticado ve solo los cursos de su semestre cuyos prerequisitos ya cumple"""
    user = AuthService.get_current_user()
    if not user or user.rol != "estudiante":
        return {"error": "Solo un estudiante puede consultar sus cursos disponibles"}, 401

    estudiante = MatriculaService.obtener_estudiante_por_user_id(user.id)
    if not estudiante:
        return {"error": "No se encontró el perfil de estudiante asociado"}, 400

    try:
        cursos, semestre_actual = CursoService.listar_disponibles_para_matricula(estudiante.id)
    except ValueError as e:
        return {"error": str(e)}, 400

    return {
        "semestre_actual": semestre_actual,
        "cursos": [_to_response(c) for c in cursos],
    }, 200


@curso_bp.get(
    "/<int:curso_id>",
    responses={"200": CursoResponse, "404": ErrorResponse},
)
def obtener_curso(path: CursoPath):
    """Obtener el detalle de un curso"""
    curso = CursoService.obtener_curso(path.curso_id)
    if not curso:
        return {"error": "Curso no encontrado"}, 404
    return _to_response(curso), 200


@curso_bp.put(
    "/<int:curso_id>",
    responses={"200": CursoResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def actualizar_curso(path: CursoPath, body: CursoUpdate):
    """Admin edita un curso existente"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede editar cursos"}, 401

    curso = CursoService.actualizar_curso(path.curso_id, body.model_dump())
    if not curso:
        return {"error": "Curso no encontrado"}, 404
    return _to_response(curso), 200


@curso_bp.delete(
    "/<int:curso_id>",
    responses={"200": {"description": "Curso eliminado"}, "401": ErrorResponse, "404": ErrorResponse},
)
def eliminar_curso(path: CursoPath):
    """Admin elimina un curso"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede eliminar cursos"}, 401

    eliminado = CursoService.eliminar_curso(path.curso_id)
    if not eliminado:
        return {"error": "Curso no encontrado"}, 404
    return {"message": "Curso eliminado correctamente"}, 200