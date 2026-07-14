from flask import request, send_file
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from ..schemas.seccion_schema import (
    SeccionCreate,
    SeccionUpdate,
    SeccionResponse,
    SeccionListResponse,
)
from ..schemas.generic_schema import ErrorResponse
from ..schemas.horario_schema import HorarioResponse
from ..services.seccion_service import SeccionService
from ..services.docente_service import DocenteService
from ..services.auth_service import AuthService
from ..services.file_service import FileService

seccion_tag = Tag(name="Sección", description="Gestión de secciones (curso + docente + periodo)")

seccion_bp = APIBlueprint("seccion", __name__, abp_tags=[seccion_tag])


class SeccionPath(BaseModel):
    seccion_id: int = Field(..., description="ID de la sección")


class SeccionQuery(BaseModel):
    curso_id: int | None = Field(None)
    docente_id: int | None = Field(None)
    periodo_academico_id: int | None = Field(None)


def _silabo_public_url(seccion):
    if not seccion.silabo_url:
        return None
    if seccion.silabo_url.startswith("http") or seccion.silabo_url.startswith("/api/"):
        return seccion.silabo_url
    return f"/api/secciones/{seccion.id}/silabo"


def _to_response(seccion):
    return SeccionResponse(
        id=seccion.id,
        curso_id=seccion.curso_id,
        curso_nombre=seccion.curso.nombre if seccion.curso else None,
        docente_id=seccion.docente_id,
        docente_nombre=f"{seccion.docente.user.nombres} {seccion.docente.user.apellidos}" if seccion.docente else None,
        periodo_academico_id=seccion.periodo_academico_id,
        nombre=seccion.nombre,
        aforo=seccion.aforo,
        silabo_url=_silabo_public_url(seccion),
        acta_validada=seccion.acta_validada,
        cupos_ocupados=SeccionService.contar_cupos_ocupados(seccion.id),
        horarios=[
            HorarioResponse(
                id=h.id,
                seccion_id=h.seccion_id,
                dia_semana=h.dia_semana,
                hora_inicio=h.hora_inicio,
                hora_final=h.hora_final,
                aula=h.aula,
            )
            for h in seccion.horarios
        ],
    ).model_dump(mode="json")


@seccion_bp.post(
    "/",
    responses={"201": SeccionResponse, "400": ErrorResponse, "401": ErrorResponse},
)
def crear_seccion(body: SeccionCreate):
    """Admin crea una sección y asigna un docente"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede crear secciones"}, 401

    try:
        seccion = SeccionService.crear_seccion(body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    return _to_response(seccion), 201


@seccion_bp.get(
    "/",
    responses={"200": SeccionListResponse},
)
def listar_secciones(query: SeccionQuery):
    """Listar secciones (filtrable por curso, docente o periodo)"""
    secciones = SeccionService.listar_secciones(
        query.curso_id, query.docente_id, query.periodo_academico_id
    )
    return [_to_response(s) for s in secciones], 200


@seccion_bp.get(
    "/<int:seccion_id>",
    responses={"200": SeccionResponse, "404": ErrorResponse},
)
def obtener_seccion(path: SeccionPath):
    """Detalle de una sección"""
    seccion = SeccionService.obtener_seccion(path.seccion_id)
    if not seccion:
        return {"error": "Sección no encontrada"}, 404
    return _to_response(seccion), 200


@seccion_bp.put(
    "/<int:seccion_id>",
    responses={"200": SeccionResponse, "400": ErrorResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def actualizar_seccion(path: SeccionPath, body: SeccionUpdate):
    """Admin reasigna docente y/o aforo de una sección"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede editar secciones"}, 401

    try:
        seccion = SeccionService.actualizar_seccion(path.seccion_id, body.model_dump())
    except ValueError as e:
        return {"error": str(e)}, 400

    if not seccion:
        return {"error": "Sección no encontrada"}, 404
    return _to_response(seccion), 200


@seccion_bp.put(
    "/<int:seccion_id>/silabo",
    responses={"200": SeccionResponse, "400": ErrorResponse, "401": ErrorResponse, "404": ErrorResponse},
)
def subir_silabo(path: SeccionPath):
    """Docente asignado a la sección sube su sílabo en PDF. Admin también puede subirlo por él."""
    user = AuthService.get_current_user()
    if not user:
        return {"error": "No hay usuario autenticado"}, 401

    seccion = SeccionService.obtener_seccion(path.seccion_id)
    if not seccion:
        return {"error": "Sección no encontrada"}, 404

    if user.rol == "docente":
        docente = DocenteService.obtener_docente_por_user_id(user.id)
        if not docente or seccion.docente_id != docente.id:
            return {"error": "No autorizado para subir el sílabo de esta sección"}, 401
    else:
        return {"error": "Solo el docente asignado puede subir el sílabo"}, 401

    archivo = request.files.get("silabo")
    try:
        stored_name = FileService.save_silabo(archivo, prefix=f"silabo-seccion-{path.seccion_id}")
    except ValueError as e:
        return {"error": str(e)}, 400

    seccion = SeccionService.subir_silabo(path.seccion_id, stored_name)
    return _to_response(seccion), 200


@seccion_bp.get(
    "/<int:seccion_id>/silabo",
    responses={"200": {"description": "Archivo PDF del sílabo"}, "401": ErrorResponse, "404": ErrorResponse},
)
def descargar_silabo(path: SeccionPath):
    """Descarga el PDF del sílabo de la sección (cualquier usuario autenticado)."""
    user = AuthService.get_current_user()
    if not user:
        return {"error": "No hay usuario autenticado"}, 401

    seccion = SeccionService.obtener_seccion(path.seccion_id)
    if not seccion:
        return {"error": "Sección no encontrada"}, 404

    if not seccion.silabo_url:
        return {"error": "Esta sección no tiene sílabo"}, 404

    if seccion.silabo_url.startswith("http"):
        return {"error": "El sílabo es una URL externa", "url": seccion.silabo_url}, 400

    path_file = FileService.get_silabo_path(seccion.silabo_url)
    if not path_file:
        return {"error": "Archivo de sílabo no encontrado"}, 404

    return send_file(
        path_file,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=path_file.name,
    )


@seccion_bp.delete(
    "/<int:seccion_id>",
    responses={"200": {"description": "Sección eliminada"}, "401": ErrorResponse, "404": ErrorResponse},
)
def eliminar_seccion(path: SeccionPath):
    """Admin elimina una sección"""
    user = AuthService.get_current_user()
    if not user or user.rol != "administrador":
        return {"error": "Solo un administrador puede eliminar secciones"}, 401

    eliminado = SeccionService.eliminar_seccion(path.seccion_id)
    if not eliminado:
        return {"error": "Sección no encontrada"}, 404
    return {"message": "Sección eliminada correctamente"}, 200