from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field

from ..schemas.periodo_academico_schema import (
    CursosPorPeriodoResponse,
    PeriodoAcademicoCreate,
    PeriodoAcademicoSearchRequest,
    PeriodoAcademicoListResponse,
    PeriodoAcademicoResponse,
    PeriodoAcademicoUpdate,
)
from ..schemas.curso_schema import CursoResponse
from ..schemas.generic_schema import ErrorResponse
from ..services.periodo_academico_service import PeriodoAcademicoService
from ..services.auth_service import AuthService

periodo_academico_tag = Tag(
    name="Periodo Académico", description="Gestión de periodos académicos"
)

periodo_academico_bp = APIBlueprint(
    "periodo_academico", __name__, abp_tags=[periodo_academico_tag]
)


class PeriodoAcademicoPath(BaseModel):
    periodo_id: int = Field(..., description="ID del periodo académico")


def _to_response(pa):
    return PeriodoAcademicoResponse(
        id=pa.id,
        semestre=pa.semestre,
        fecha_inicio=pa.fecha_inicio.isoformat(),
        fecha_fin=pa.fecha_fin.isoformat(),
        estado=pa.estado,
        requiere_pago=bool(pa.requiere_pago),
    ).model_dump()


@periodo_academico_bp.get("", responses={"200": PeriodoAcademicoListResponse})
def search_periodos_academicos(query: PeriodoAcademicoSearchRequest):
    """Buscar periodos académicos."""

    result = PeriodoAcademicoService.search(query)

    return (
        PeriodoAcademicoListResponse(
            root=[_to_response(pa) for pa in result]
        ).model_dump(),
        200,
    )


@periodo_academico_bp.get(
    "/<int:periodo_id>",
    responses={"200": PeriodoAcademicoResponse, "404": ErrorResponse},
)
def get_periodo_academico(path: PeriodoAcademicoPath):
    """Obtener un periodo académico por su ID."""

    periodo = PeriodoAcademicoService.get_by_id(path.periodo_id)

    if not periodo:
        return {"message": "Periodo académico no encontrado"}, 404

    return _to_response(periodo), 200


@periodo_academico_bp.get(
    "/<int:periodo_id>/cursos",
    responses={"200": CursosPorPeriodoResponse, "404": ErrorResponse},
)
def get_cursos_by_periodo_academico(path: PeriodoAcademicoPath):
    """Obtener los cursos asociados a un periodo académico."""

    cursos = PeriodoAcademicoService.get_cursos_by_periodo(path.periodo_id)

    if cursos is None:
        return {"message": "Periodo académico no encontrado"}, 404

    return (
        CursosPorPeriodoResponse(
            root=[
                CursoResponse(
                    id=curso.id,
                    plan_estudios_id=curso.plan_estudios_id,
                    nombre=curso.nombre,
                    horas_teoria=curso.horas_teoria,
                    horas_practica=curso.horas_practica,
                    semestre_num=curso.semestre_num,
                    prerequisitos_ids=[prereq.id for prereq in curso.prerequisitos],
                )
                for curso in cursos
            ]
        ).model_dump(),
        200,
    )


@periodo_academico_bp.post(
    "",
    responses={"201": PeriodoAcademicoResponse, "401": ErrorResponse},
)
def crear_periodo_academico(body: PeriodoAcademicoCreate):
    """Admin o dirección crea un nuevo periodo académico."""

    user = AuthService.get_current_user()
    if not user or user.rol not in ("administrador", "direccion"):
        return {"message": "No autorizado para crear periodos académicos"}, 401

    periodo = PeriodoAcademicoService.create(body.model_dump())
    return _to_response(periodo), 201


@periodo_academico_bp.put(
    "/<int:periodo_id>",
    responses={
        "200": PeriodoAcademicoResponse,
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def actualizar_periodo_academico(
    path: PeriodoAcademicoPath, body: PeriodoAcademicoUpdate
):
    """Admin o dirección actualiza un periodo (incluye requiere_pago)."""

    user = AuthService.get_current_user()
    if not user or user.rol not in ("administrador", "direccion"):
        return {
            "message": "No autorizado para editar periodos académicos"
        }, 401

    periodo = PeriodoAcademicoService.update(
        path.periodo_id, body.model_dump(exclude_unset=True)
    )
    if not periodo:
        return {"message": "Periodo académico no encontrado"}, 404

    return _to_response(periodo), 200


@periodo_academico_bp.delete(
    "/<int:periodo_id>",
    responses={
        "200": {"description": "Periodo académico eliminado"},
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def eliminar_periodo_academico(path: PeriodoAcademicoPath):
    """Admin elimina un periodo académico."""

    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {
            "message": "Solo un administrador puede eliminar periodos académicos"
        }, 401

    eliminado = PeriodoAcademicoService.delete(path.periodo_id)
    if not eliminado:
        return {"message": "Periodo académico no encontrado"}, 404

    return {"message": "Periodo académico eliminado correctamente"}, 200


@periodo_academico_bp.get(
    "/me", responses={"200": PeriodoAcademicoListResponse, "401": ErrorResponse}
)
def get_periodo_academico_estudiante_matriculado():
    """Obtener los periodos académicos en los que el estudiante actual está matriculado."""
    user = AuthService.get_current_user()
    if not user or user.rol != "estudiante":
        return {
            "message": "Solo un estudiante puede acceder a sus periodos académicos"
        }, 401

    periodos = PeriodoAcademicoService.get_periodos_academicos_estudiante(user.id)

    return (
        PeriodoAcademicoListResponse(
            root=[_to_response(pa) for pa in periodos]
        ).model_dump(),
        200,
    )
