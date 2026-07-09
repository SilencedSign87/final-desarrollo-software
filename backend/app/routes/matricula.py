from flask import session, send_file
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from ..schemas.matricula_schema import (
    MatriculaCreate,
    MatriculaValidar,
    MatriculaResponse,
    MatriculaListResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.matricula_service import MatriculaService
from ..services.auth_service import AuthService

matricula_tag = Tag(name="Matrícula", description="Gestión de matrícula de estudiantes")

matricula_bp = APIBlueprint("matricula", __name__, abp_tags=[matricula_tag])


class MatriculaPath(BaseModel):
    matricula_id: int = Field(..., description="ID de la matrícula")


class MatriculaQuery(BaseModel):
    estado: str | None = Field(None, description="Filtrar por estado")


def _to_response(matricula):
    return MatriculaResponse(
        id=matricula.id,
        periodo_academico_id=matricula.periodo_academico_id,
        estudiante_id=matricula.estudiante_id,
        estado=matricula.estado,
        observacion=matricula.observacion,
        comprobante_url=matricula.comprobante_url,
        validado_user_id=matricula.validado_user_id,
        detalles=[
            {
                "id": d.id,
                "seccion_id": d.seccion_id,
                "estado_curso": d.estado_curso,
            }
            for d in matricula.detalles
        ],
    ).model_dump()


@matricula_bp.post(
    "/",
    responses={"201": MatriculaResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def crear_matricula(body: MatriculaCreate):
    """Estudiante solicita una nueva matrícula"""
    user = AuthService.get_current_user()
    if not user or user.rol != "estudiante":
        return {"error": "Solo un estudiante puede solicitar matrícula"}, 401

    estudiante = MatriculaService.obtener_estudiante_por_user_id(user.id)
    if not estudiante:
        return {"error": "No se encontró el perfil de estudiante asociado"}, 400

    try:
        matricula = MatriculaService.crear_matricula(estudiante.id, body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    return _to_response(matricula), 201


@matricula_bp.get(
    "/",
    responses={"200": MatriculaListResponse, "401": ErrorResponse},
)
def listar_matriculas(query: MatriculaQuery):
    """Listar matrículas (opcionalmente filtradas por estado). Uso: admin/dirección."""
    user = AuthService.get_current_user()
    if not user or user.rol not in ("administrador", "direccion"):
        return {"error": "No autorizado"}, 401

    matriculas = MatriculaService.listar_matriculas(query.estado)
    return [_to_response(m) for m in matriculas], 200


@matricula_bp.get(
    "/<int:matricula_id>",
    responses={"200": MatriculaResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def obtener_matricula(path: MatriculaPath):
    """Obtener el detalle de una matrícula"""
    user = AuthService.get_current_user()
    if not user:
        return {"error": "No hay usuario autenticado"}, 401

    matricula = MatriculaService.obtener_matricula(path.matricula_id)
    if not matricula:
        return {"error": "Matrícula no encontrada"}, 404

    if user.rol == "estudiante":
        estudiante = MatriculaService.obtener_estudiante_por_user_id(user.id)
        if not estudiante or matricula.estudiante_id != estudiante.id:
            return {"error": "No autorizado para ver esta matrícula"}, 401

    return _to_response(matricula), 200


@matricula_bp.put(
    "/<int:matricula_id>/validar",
    responses={"200": MatriculaResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def validar_matricula(path: MatriculaPath, body: MatriculaValidar):
    """Admin valida o rechaza una matrícula"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede validar matrículas"}, 401

    matricula = MatriculaService.validar_matricula(
        path.matricula_id, user.id, body.model_dump()
    )
    if not matricula:
        return {"error": "Matrícula no encontrada"}, 404

    return _to_response(matricula), 200


@matricula_bp.get(
    "/estadisticas",
    responses={"200": {"description": "Conteo de matrículas por estado"}, "401": ErrorResponse},
)
def estadisticas():
    """Dirección consulta estadísticas de matrícula"""
    user = AuthService.get_current_user()
    if not user or user.rol != "direccion":
        return {"error": "No autorizado"}, 401

    return MatriculaService.estadisticas(), 200


@matricula_bp.get(
    "/<int:matricula_id>/ficha",
    responses={
        "200": {"description": "Archivo PDF de la ficha de matrícula"},
        "400": ErrorResponse,
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def descargar_ficha(path: MatriculaPath):
    """Descarga la ficha de matrícula en PDF. El estudiante solo puede descargar la suya."""
    user = AuthService.get_current_user()
    if not user:
        return {"error": "No hay usuario autenticado"}, 401

    matricula = MatriculaService.obtener_matricula(path.matricula_id)
    if not matricula:
        return {"error": "Matrícula no encontrada"}, 404

    if user.rol == "estudiante":
        estudiante = MatriculaService.obtener_estudiante_por_user_id(user.id)
        if not estudiante or matricula.estudiante_id != estudiante.id:
            return {"error": "No autorizado para descargar esta ficha"}, 401
    elif user.rol not in ("administrador", "direccion"):
        return {"error": "No autorizado"}, 401

    try:
        buffer = MatriculaService.generar_ficha_pdf(path.matricula_id)
    except ValueError as e:
        return {"error": str(e)}, 400

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"ficha_matricula_{path.matricula_id}.pdf",
    )