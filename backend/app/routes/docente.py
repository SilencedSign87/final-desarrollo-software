from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from ..schemas.docente_schema import (
    DocenteCreate,
    DocenteUpdate,
    DocenteResponse,
    DocenteListResponse,
    SeccionesDocenteListResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..services.docente_service import DocenteService
from ..services.auth_service import AuthService

docente_tag = Tag(name="Docente", description="Gestión de docentes y su carga académica")

docente_bp = APIBlueprint("docente", __name__, abp_tags=[docente_tag])


class DocentePath(BaseModel):
    docente_id: int = Field(..., description="ID del docente")


def _to_response(docente):
    return DocenteResponse(
        id=docente.id,
        user_id=docente.user_id,
        categoria=docente.categoria,
        total_secciones=len(docente.secciones),
    ).model_dump()


def _seccion_to_response(seccion):
    return {
        "id": seccion.id,
        "curso_id": seccion.curso_id,
        "nombre": seccion.nombre,
        "periodo_academico_id": seccion.periodo_academico_id,
        "aforo": seccion.aforo,
        "silabo_url": seccion.silabo_url,
    }


@docente_bp.post(
    "/",
    responses={"201": DocenteResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def crear_docente(body: DocenteCreate):
    """Admin crea el perfil de docente para un usuario ya registrado con rol 'docente'"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede crear perfiles de docente"}, 401

    try:
        docente = DocenteService.crear_docente(body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    return _to_response(docente), 201


@docente_bp.get(
    "/",
    responses={"200": DocenteListResponse, "401": ErrorResponse},
)
def listar_docentes():
    """Listar todos los docentes. Uso: admin/dirección."""
    user = AuthService.get_current_user()
    if not user or user.rol not in ("administrador", "direccion"):
        return {"error": "No autorizado"}, 401

    docentes = DocenteService.listar_docentes()
    return [_to_response(d) for d in docentes], 200


@docente_bp.get(
    "/me",
    responses={"200": DocenteResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def mi_perfil_docente():
    """El docente autenticado obtiene su propio perfil (id, categoría, etc.)"""
    user = AuthService.get_current_user()
    if not user or user.rol != "docente":
        return {"error": "Solo un docente puede consultar su perfil"}, 401

    docente = DocenteService.obtener_docente_por_user_id(user.id)
    if not docente:
        return {"error": "No se encontró el perfil de docente asociado a este usuario"}, 400

    return _to_response(docente), 200


@docente_bp.get(
    "/<int:docente_id>",
    responses={"200": DocenteResponse, "404": ErrorResponse},
)
def obtener_docente(path: DocentePath):
    """Obtener el detalle de un docente"""
    docente = DocenteService.obtener_docente(path.docente_id)
    if not docente:
        return {"error": "Docente no encontrado"}, 404
    return _to_response(docente), 200


@docente_bp.put(
    "/<int:docente_id>",
    responses={"200": DocenteResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def actualizar_docente(path: DocentePath, body: DocenteUpdate):
    """Admin edita la categoría de un docente"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede editar docentes"}, 401

    docente = DocenteService.actualizar_docente(path.docente_id, body.model_dump())
    if not docente:
        return {"error": "Docente no encontrado"}, 404
    return _to_response(docente), 200


@docente_bp.get(
    "/<int:docente_id>/secciones",
    responses={"200": SeccionesDocenteListResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def secciones_de_docente(path: DocentePath):
    """Docente ve sus cursos/secciones asignados. También accesible por admin/dirección."""
    user = AuthService.get_current_user()
    if not user:
        return {"error": "No hay usuario autenticado"}, 401

    docente = DocenteService.obtener_docente(path.docente_id)
    if not docente:
        return {"error": "Docente no encontrado"}, 404

    if user.rol == "docente" and docente.user_id != user.id:
        return {"error": "No autorizado para ver estas secciones"}, 401

    secciones = DocenteService.secciones_de_docente(path.docente_id)
    return [_seccion_to_response(s) for s in secciones], 200


@docente_bp.get(
    "/carga-docente",
    responses={"200": {"description": "Carga (número de secciones) por docente"}, "401": ErrorResponse},
)
def carga_docente():
    """Dirección evalúa la carga docente (secciones asignadas por docente)"""
    user = AuthService.get_current_user()
    if not user or user.rol != "direccion":
        return {"error": "No autorizado"}, 401

    return DocenteService.carga_docente(), 200