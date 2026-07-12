from flask import g
from flask_openapi3 import APIBlueprint, Tag

from ..extensions import db
from ..middleware import auth_required, roles_required
from ..models.auditoria_log import AuditoriaLog
from ..models.solicitud_documento import SolicitudDocumento
from ..models.user import User
from ..schemas.generic_schema import ErrorResponse
from ..schemas.security_schema import (
    AuditoriaLogQuery,
    AuditoriaLogResponse,
    AuditReportResponse,
    RoleUpdate,
    UserIdPath,
)
from ..schemas.user_schema import UserResponse
from ..services.audit_service import AuditService

security_tag = Tag(
    name="Administracion y Seguridad",
    description="Roles, permisos, auditorias y reportes estrategicos",
)

security_bp = APIBlueprint("security", __name__, abp_tags=[security_tag])


def _serialize_user(user):
    return UserResponse(
        id=user.id,
        nombres=user.nombres,
        apellidos=user.apellidos,
        email=user.email,
        rol=user.rol,
    ).model_dump()


def _serialize_log(entry: AuditoriaLog):
    return AuditoriaLogResponse(
        id=entry.id,
        user_id=entry.user_id,
        usuario_email=entry.usuario_email,
        accion=entry.accion,
        recurso=entry.recurso,
        detalle=entry.detalle,
        fecha_creacion=entry.fecha_creacion.isoformat() if entry.fecha_creacion else "",
    ).model_dump()


@security_bp.get(
    "/roles",
    responses={"200": {"description": "Listado de roles disponibles"}, "401": ErrorResponse},
)
@auth_required
def list_roles():
    """Listar perfiles de acceso disponibles."""
    return {
        "data": ["estudiante", "docente", "administrador", "direccion"],
    }, 200


@security_bp.get(
    "/usuarios",
    responses={"200": {"description": "Listado de usuarios"}, "403": ErrorResponse},
)
@roles_required("administrador")
def list_users():
    """Listar usuarios para gestion de perfiles de acceso."""
    users = User.query.order_by(User.id.asc()).all()
    return {"data": [_serialize_user(user) for user in users]}, 200


@security_bp.put(
    "/usuarios/<int:user_id>/rol",
    responses={"200": UserResponse, "403": ErrorResponse, "404": ErrorResponse},
)
@roles_required("administrador")
def update_user_role(path: UserIdPath, body: RoleUpdate):
    """Definir o actualizar el perfil de acceso de un usuario."""
    user = User.query.get(path.user_id)
    if not user:
        return {"error": "Usuario no encontrado"}, 404

    rol_anterior = user.rol
    if rol_anterior == body.rol:
        return _serialize_user(user), 200

    user.rol = body.rol
    AuditService.log(
        accion="cambio_rol",
        recurso=f"user:{user.id}",
        detalle=(
            f"{user.email}: {rol_anterior} → {body.rol} "
            f"(por {g.current_user.email})"
        ),
        user=g.current_user,
    )
    db.session.commit()

    return _serialize_user(user), 200


@security_bp.get(
    "/auditorias/resumen",
    responses={"200": AuditReportResponse, "403": ErrorResponse},
)
@roles_required("direccion")
def audit_summary():
    """Consultar resumen de auditorias y metricas estrategicas."""
    total_solicitudes = SolicitudDocumento.query.count()
    documentos_pendientes = SolicitudDocumento.query.filter(
        SolicitudDocumento.estado.in_(["pendiente_autorizacion", "autorizado"])
    ).count()
    documentos_emitidos = SolicitudDocumento.query.filter_by(estado="emitido").count()

    return (
        AuditReportResponse(
            total_usuarios=User.query.count(),
            total_solicitudes_documento=total_solicitudes,
            documentos_pendientes=documentos_pendientes,
            documentos_emitidos=documentos_emitidos,
            total_eventos_auditoria=AuditoriaLog.query.count(),
            cambios_rol=AuditoriaLog.query.filter_by(accion="cambio_rol").count(),
        ).model_dump(),
        200,
    )


@security_bp.get(
    "/auditorias/logs",
    responses={"200": {"description": "Bitácora cronológica"}, "403": ErrorResponse},
)
@roles_required("direccion")
def audit_logs(query: AuditoriaLogQuery):
    """Listar bitácora inmutable de acciones críticas."""
    pagination = AuditService.list_logs(
        page=query.page,
        per_page=query.per_page,
        accion=query.accion,
    )
    return {
        "data": [_serialize_log(entry) for entry in pagination.items],
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    }, 200


@security_bp.get(
    "/auditorias/cambios-rol",
    responses={"200": {"description": "Historial de cambios de rol"}, "403": ErrorResponse},
)
@roles_required("direccion")
def role_change_history(query: AuditoriaLogQuery):
    """Historial de cambios de rol (subset de la bitácora)."""
    pagination = AuditService.list_role_changes(page=query.page, per_page=query.per_page)
    return {
        "data": [_serialize_log(entry) for entry in pagination.items],
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    }, 200
