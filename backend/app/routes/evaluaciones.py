from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from ..schemas.evaluacion_schema import (
    EvaluacionCreate,
    EvaluacionUpdate,
    EvaluacionResponse,
    EvaluacionListResponse,
    NotasSeccionResponse,
    TipoEvaluacionCreate,
    TipoEvaluacionUpdate,
    TipoEvaluacionResponse,
    TipoEvaluacionListResponse,
    EstudianteSimpleResponse,
    NotasEstudianteListResponse,
    RecordAcademicoResponse,
    EstadisticasNotasResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.evaluacion_service import EvaluacionService, TipoEvaluacionService
from ..services.auth_service import AuthService

evaluaciones_tag = Tag(name="Evaluaciones", description="Gestión de evaluaciones")
evaluaciones_bp = APIBlueprint("evaluaciones", __name__, abp_tags=[evaluaciones_tag])


class EvaluacionPath(BaseModel):
    evaluacion_id: int = Field(..., description="ID de la evaluación")


class EvaluacionQuery(BaseModel):
    tipo_evaluacion_id: int | None = Field(
        None, description="Filtrar por tipo de evaluación"
    )
    detalle_matricula_id: int | None = Field(
        None, description="Filtrar por detalle de matrícula"
    )


class TipoEvaluacionPath(BaseModel):
    tipo_evaluacion_id: int = Field(..., description="ID del tipo de evaluación")


class TipoEvaluacionQuery(BaseModel):
    seccion_id: int | None = Field(None, description="Filtrar por ID de sección")
    nombre: str | None = Field(None, description="Buscar por nombre")
    evaluacion_id: int | None = Field(None, description="Filtrar por ID de evaluación")


def _to_response(evaluacion):
    return EvaluacionResponse(
        id=evaluacion.id,
        tipo_evaluacion_id=evaluacion.tipo_evaluacion_id,
        detalle_matricula_id=evaluacion.detalle_matricula_id,
        nota=evaluacion.nota,
    ).model_dump()


@evaluaciones_bp.post(
    "",
    responses={"201": EvaluacionResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def crear_evaluacion(body: EvaluacionCreate):
    """Crear una evaluación"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador" and user.rol != "docente":
        return {"error": "No autorizado"}, 401

    try:
        evaluacion = EvaluacionService.crear_evaluacion(body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    return _to_response(evaluacion), 201


@evaluaciones_bp.get(
    "",
    responses={"200": EvaluacionListResponse},
)
def listar_evaluaciones(query: EvaluacionQuery):
    """Listar evaluaciones"""
    evaluaciones = EvaluacionService.listar_evaluaciones(
        tipo_evaluacion_id=query.tipo_evaluacion_id,
        detalle_matricula_id=query.detalle_matricula_id,
    )
    return [_to_response(e) for e in evaluaciones], 200


@evaluaciones_bp.get(
    "/<int:evaluacion_id>",
    responses={"200": EvaluacionResponse, "404": ErrorResponse},
)
def obtener_evaluacion(path: EvaluacionPath):
    """Detalle de una evaluación"""
    evaluacion = EvaluacionService.obtener_evaluacion(path.evaluacion_id)
    if not evaluacion:
        return {"error": "Evaluación no encontrada"}, 404
    return _to_response(evaluacion), 200


@evaluaciones_bp.put(
    "/<int:evaluacion_id>",
    responses={
        "200": EvaluacionResponse,
        "400": ErrorResponse,
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def actualizar_evaluacion(path: EvaluacionPath, body: EvaluacionUpdate):
    """Actualizar nota de una evaluación"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador" and user.rol != "docente":
        return {"error": "No autorizado"}, 401

    try:
        evaluacion = EvaluacionService.actualizar_evaluacion(
            path.evaluacion_id, body.model_dump()
        )
    except ValueError as e:
        return {"error": str(e)}, 400

    if not evaluacion:
        return {"error": "Evaluación no encontrada"}, 404
    return _to_response(evaluacion), 200


@evaluaciones_bp.delete(
    "/<int:evaluacion_id>",
    responses={
        "200": {"description": "Evaluación eliminada"},
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def eliminar_evaluacion(path: EvaluacionPath):
    """Eliminar una evaluación"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "No autorizado"}, 401

    eliminado = EvaluacionService.eliminar_evaluacion(path.evaluacion_id)
    if not eliminado:
        return {"error": "Evaluación no encontrada"}, 404
    return {"message": "Evaluación eliminada correctamente"}, 200


@evaluaciones_bp.post(
    "/tipo-evaluaciones",
    responses={
        "201": TipoEvaluacionResponse,
        "400": ErrorResponse,
        "401": ErrorResponse,
    },
)
def crear_tipo_evaluacion(body: TipoEvaluacionCreate):
    """Crear un tipo de evaluación"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador" and user.rol != "docente":
        return {"error": "No autorizado"}, 401

    try:
        tipo = TipoEvaluacionService.crear_tipo_evaluacion(body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    return (
        TipoEvaluacionResponse(
            id=tipo.id, seccion_id=tipo.seccion_id, nombre=tipo.nombre, peso=tipo.peso
        ).model_dump(),
        201,
    )


@evaluaciones_bp.get(
    "/tipo-evaluaciones/<int:tipo_evaluacion_id>",
    responses={"200": TipoEvaluacionResponse, "404": ErrorResponse},
)
def obtener_tipo_evaluacion(path: TipoEvaluacionPath):
    """Detalle de un tipo de evaluación"""
    tipo = TipoEvaluacionService.obtener_tipo_evaluacion(path.tipo_evaluacion_id)
    if not tipo:
        return {"error": "Tipo de evaluación no encontrado"}, 404
    return (
        TipoEvaluacionResponse(
            id=tipo.id, seccion_id=tipo.seccion_id, nombre=tipo.nombre, peso=tipo.peso
        ).model_dump(),
        200,
    )


@evaluaciones_bp.put(
    "/tipo-evaluaciones/<int:tipo_evaluacion_id>",
    responses={
        "200": TipoEvaluacionResponse,
        "400": ErrorResponse,
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def actualizar_tipo_evaluacion(path: TipoEvaluacionPath, body: TipoEvaluacionUpdate):
    """Actualizar un tipo de evaluación"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador" and user.rol != "docente":
        return {"error": "No autorizado"}, 401

    try:
        tipo = TipoEvaluacionService.actualizar_tipo_evaluacion(
            path.tipo_evaluacion_id, body.model_dump()
        )
    except ValueError as e:
        return {"error": str(e)}, 400

    if not tipo:
        return {"error": "Tipo de evaluación no encontrado"}, 404
    return (
        TipoEvaluacionResponse(
            id=tipo.id, seccion_id=tipo.seccion_id, nombre=tipo.nombre, peso=tipo.peso
        ).model_dump(),
        200,
    )


@evaluaciones_bp.delete(
    "/tipo-evaluaciones/<int:tipo_evaluacion_id>",
    responses={
        "200": {"description": "Tipo de evaluación eliminado"},
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def eliminar_tipo_evaluacion(path: TipoEvaluacionPath):
    """Eliminar un tipo de evaluación"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador" and user.rol != "docente":
        return {"error": "No autorizado"}, 401

    eliminado = TipoEvaluacionService.eliminar_tipo_evaluacion(path.tipo_evaluacion_id)
    if not eliminado:
        return {"error": "Tipo de evaluación no encontrado"}, 404
    return {"message": "Tipo de evaluación eliminado correctamente"}, 200


@evaluaciones_bp.get(
    "/tipo-evaluaciones",
    responses={"200": TipoEvaluacionListResponse},
)
def listar_tipos_evaluacion(query: TipoEvaluacionQuery):
    """Listar tipos de evaluación"""
    tipos = TipoEvaluacionService.listar_tipos_evaluacion(
        seccion_id=query.seccion_id,
        nombre=query.nombre,
        evaluacion_id=query.evaluacion_id,
    )
    return [
        TipoEvaluacionResponse(
            id=t.id, seccion_id=t.seccion_id, nombre=t.nombre, peso=t.peso
        ).model_dump()
        for t in tipos
    ], 200


@evaluaciones_bp.get(
    "/<int:evaluacion_id>/estudiante",
    responses={
        "200": EstudianteSimpleResponse,
        "404": ErrorResponse,
    },
)
def obtener_estudiante_de_evaluacion(path: EvaluacionPath):
    """Obtener el estudiante asociado a una evaluación"""
    estudiante = EvaluacionService.obtener_estudiante(path.evaluacion_id)
    if not estudiante:
        return {"error": "Evaluación no encontrada"}, 404
    return (
        EstudianteSimpleResponse(
            id=estudiante.id,
            user_id=estudiante.user_id,
            plan_estudios_id=estudiante.plan_estudios_id,
        ).model_dump(),
        200,
    )


class SeccionPath(BaseModel):
    seccion_id: int = Field(..., description="ID de la sección")


class ValidarPromedioBody(BaseModel):
    detalle_matricula_id: int = Field(
        ..., description="ID del detalle de matrícula"
    )


@evaluaciones_bp.post(
    "/seccion/<int:seccion_id>/validar-promedio",
    responses={
        "200": {"description": "Promedio validado y guardado"},
        "400": ErrorResponse,
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def validar_promedio(path: SeccionPath, body: ValidarPromedioBody):
    """Calcular y guardar el promedio final de un estudiante"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "No autorizado"}, 401

    try:
        promedio = EvaluacionService.validar_promedio(body.detalle_matricula_id)
    except ValueError as e:
        return {"error": str(e)}, 400

    return {"promedio_final": promedio, "message": "Promedio validado correctamente"}, 200


@evaluaciones_bp.get(
    "/seccion/<int:seccion_id>/notas",
    responses={"200": NotasSeccionResponse, "404": ErrorResponse},
)
def listar_notas_por_seccion(path: SeccionPath):
    """Listar estudiantes con sus notas por tipo de evaluación para una sección"""
    from ..models.seccion import Seccion

    seccion = Seccion.query.get(path.seccion_id)
    if not seccion:
        return {"error": "Sección no encontrada"}, 404

    resultados = EvaluacionService.listar_notas_por_seccion(path.seccion_id)
    return resultados, 200


class DireccionEstadisticasQuery(BaseModel):
    periodo_academico_id: int = Field(..., description="ID del periodo académico")
    curso_id: int | None = Field(None, description="Filtrar por curso")
    seccion_id: int | None = Field(None, description="Filtrar por sección")


class NotasEstudianteQuery(BaseModel):
    periodo_academico_id: int = Field(..., description="ID del periodo académico")


@evaluaciones_bp.get(
    "/estudiante/mis-notas",
    responses={
        "200": NotasEstudianteListResponse,
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def listar_notas_estudiante(query: NotasEstudianteQuery):
    """Listar notas del estudiante actual en un periodo académico"""
    user = AuthService.get_current_user()
    if not user or user.rol != "estudiante":
        return {"error": "No autorizado"}, 401

    estudiante = user.estudiante
    if not estudiante:
        return {"error": "Perfil de estudiante no encontrado"}, 404

    notas = EvaluacionService.listar_notas_estudiante(
        estudiante.id, query.periodo_academico_id
    )
    return notas, 200


@evaluaciones_bp.get(
    "/direccion/estadisticas",
    responses={
        "200": EstadisticasNotasResponse,
        "400": ErrorResponse,
        "401": ErrorResponse,
    },
)
def estadisticas_notas_direccion(query: DireccionEstadisticasQuery):
    """Dirección consulta estadísticas de notas por periodo académico."""
    user = AuthService.get_current_user()
    if not user or user.rol != "direccion":
        return {"error": "No autorizado"}, 401

    stats = EvaluacionService.estadisticas_notas(
        periodo_academico_id=query.periodo_academico_id,
        curso_id=query.curso_id,
        seccion_id=query.seccion_id,
    )
    return stats, 200


@evaluaciones_bp.get(
    "/estudiante/record-academico",
    responses={
        "200": RecordAcademicoResponse,
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def record_academico():
    """Obtener el record académico completo del estudiante"""
    user = AuthService.get_current_user()
    if not user or user.rol != "estudiante":
        return {"error": "No autorizado"}, 401

    estudiante = user.estudiante
    if not estudiante:
        return {"error": "Perfil de estudiante no encontrado"}, 404

    record = EvaluacionService.record_academico(estudiante.id)
    return record, 200
