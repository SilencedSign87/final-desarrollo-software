import json

from flask import request, send_file
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from ..schemas.matricula_schema import (
    MatriculaValidar,
    MatriculaResponse,
    MatriculaListResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.matricula_service import MatriculaService
from ..services.auth_service import AuthService
from ..services.file_service import FileService

matricula_tag = Tag(name="Matrícula", description="Gestión de matrícula de estudiantes")

matricula_bp = APIBlueprint("matricula", __name__, abp_tags=[matricula_tag])


class MatriculaPath(BaseModel):
    matricula_id: int = Field(..., description="ID de la matrícula")


class MatriculaQuery(BaseModel):
    estado: str | None = Field(None, description="Filtrar por estado")


def _comprobante_public_url(matricula):
    if not matricula.comprobante_url:
        return None
    if matricula.comprobante_url.startswith("http") or matricula.comprobante_url.startswith("/api/"):
        return matricula.comprobante_url
    return f"/api/matriculas/{matricula.id}/comprobante"


def _to_response(matricula):
    estudiante = matricula.estudiante
    periodo = matricula.periodo_academico
    return MatriculaResponse(
        id=matricula.id,
        periodo_academico_id=matricula.periodo_academico_id,
        periodo_semestre=periodo.semestre if periodo else None,
        periodo_requiere_pago=bool(periodo.requiere_pago) if periodo else False,
        estudiante_id=matricula.estudiante_id,
        estudiante_nombre=f"{estudiante.user.nombres} {estudiante.user.apellidos}" if estudiante and estudiante.user else None,
        estado=matricula.estado,
        observacion=matricula.observacion,
        comprobante_url=_comprobante_public_url(matricula),
        validado_user_id=matricula.validado_user_id,
        validador_nombre=f"{matricula.validador.nombres} {matricula.validador.apellidos}" if matricula.validador else None,
        detalles=[
            {
                "id": d.id,
                "seccion_id": d.seccion_id,
                "seccion_nombre": d.seccion.nombre if d.seccion else None,
                "curso_nombre": d.seccion.curso.nombre if d.seccion and d.seccion.curso else None,
                "estado_curso": d.estado_curso,
            }
            for d in matricula.detalles
        ],
    ).model_dump()


def _parse_secciones_ids():
    raw = request.form.get("secciones_ids") or request.form.get("secciones_ids[]")
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [int(x) for x in parsed]
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        return [int(x) for x in request.form.getlist("secciones_ids") if x]

    values = request.form.getlist("secciones_ids")
    if values:
        return [int(x) for x in values]
    return []


@matricula_bp.post(
    "/",
    responses={"201": MatriculaResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def crear_matricula():
    """Estudiante solicita una nueva matrícula (JSON o multipart con comprobante)."""
    user = AuthService.get_current_user()
    if not user or user.rol != "estudiante":
        return {"error": "Solo un estudiante puede solicitar matrícula"}, 401

    estudiante = MatriculaService.obtener_estudiante_por_user_id(user.id)
    if not estudiante:
        return {"error": "No se encontró el perfil de estudiante asociado"}, 400

    comprobante_file = None
    if request.content_type and "multipart/form-data" in request.content_type:
        try:
            periodo_academico_id = int(request.form.get("periodo_academico_id"))
        except (TypeError, ValueError):
            return {"error": "periodo_academico_id es obligatorio"}, 400

        try:
            secciones_ids = _parse_secciones_ids()
        except ValueError:
            return {"error": "secciones_ids inválidas"}, 400

        if not secciones_ids:
            return {"error": "Debes seleccionar al menos una sección"}, 400

        data = {
            "periodo_academico_id": periodo_academico_id,
            "secciones_ids": secciones_ids,
            "comprobante_url": request.form.get("comprobante_url") or None,
        }
        comprobante_file = request.files.get("comprobante")
    else:
        body = request.get_json(silent=True) or {}
        if "periodo_academico_id" not in body or "secciones_ids" not in body:
            return {"error": "periodo_academico_id y secciones_ids son obligatorios"}, 400
        data = {
            "periodo_academico_id": int(body["periodo_academico_id"]),
            "secciones_ids": [int(x) for x in body["secciones_ids"]],
            "comprobante_url": body.get("comprobante_url"),
        }

    try:
        matricula = MatriculaService.crear_matricula(
            estudiante.id, data, comprobante_file=comprobante_file
        )
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
    "/mias",
    responses={"200": MatriculaListResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def mis_matriculas():
    """El estudiante autenticado ve únicamente sus propias matrículas"""
    user = AuthService.get_current_user()
    if not user or user.rol != "estudiante":
        return {"error": "Solo un estudiante puede consultar sus propias matrículas"}, 401

    estudiante = MatriculaService.obtener_estudiante_por_user_id(user.id)
    if not estudiante:
        return {"error": "No se encontró el perfil de estudiante asociado"}, 400

    matriculas = MatriculaService.listar_matriculas_por_estudiante(estudiante.id)
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


@matricula_bp.get(
    "/<int:matricula_id>/comprobante",
    responses={
        "200": {"description": "Archivo del comprobante de pago"},
        "401": ErrorResponse,
        "404": ErrorResponse,
    },
)
def descargar_comprobante(path: MatriculaPath):
    """Descarga el comprobante de pago adjunto a la matrícula."""
    user = AuthService.get_current_user()
    if not user:
        return {"error": "No hay usuario autenticado"}, 401

    matricula = MatriculaService.obtener_matricula(path.matricula_id)
    if not matricula:
        return {"error": "Matrícula no encontrada"}, 404

    if user.rol == "estudiante":
        estudiante = MatriculaService.obtener_estudiante_por_user_id(user.id)
        if not estudiante or matricula.estudiante_id != estudiante.id:
            return {"error": "No autorizado"}, 401
    elif user.rol not in ("administrador", "direccion"):
        return {"error": "No autorizado"}, 401

    if not matricula.comprobante_url:
        return {"error": "Esta matrícula no tiene comprobante"}, 404

    if matricula.comprobante_url.startswith("http"):
        return {"error": "El comprobante es una URL externa", "url": matricula.comprobante_url}, 400

    path_file = FileService.get_comprobante_path(matricula.comprobante_url)
    if not path_file:
        return {"error": "Archivo de comprobante no encontrado"}, 404

    return send_file(
        path_file,
        mimetype=FileService.mimetype_for(path_file.name),
        as_attachment=True,
        download_name=path_file.name,
    )


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
