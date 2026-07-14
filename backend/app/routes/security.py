from flask import current_app, g
from flask_openapi3 import APIBlueprint, Tag

from ..extensions import db
from ..middleware import auth_required, roles_required
from ..models.auditoria_log import AuditoriaLog
from ..models.docente import Docente
from ..models.estudiante import Estudiante
from ..models.plan_estudio import PlanEstudio
from ..models.solicitud_documento import SolicitudDocumento
from ..models.user import User
from ..schemas.generic_schema import ErrorResponse
from ..schemas.security_schema import (
    AdminUserCreate,
    AuditoriaLogQuery,
    AuditoriaLogResponse,
    AuditReportResponse,
    RoleUpdate,
    UserIdPath,
)
from ..schemas.user_schema import UserResponse
from ..services.audit_service import AuditService
from ..services.auth_service import AuthService
from ..utils.datetime_utils import format_lima

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
        fecha_creacion=format_lima(entry.fecha_creacion),
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


@security_bp.post(
    "/usuarios/crear",
    responses={"201": UserResponse, "400": ErrorResponse, "403": ErrorResponse},
)
@roles_required("administrador")
def create_user(body: AdminUserCreate):
    """Crear un usuario del sistema (y su perfil academico si aplica)."""
    if User.query.filter_by(email=body.email).first():
        return {"error": "El correo electrónico ya está registrado"}, 400
    if User.query.filter_by(dni=body.dni).first():
        return {"error": "El DNI ya está registrado"}, 400

    if body.rol == "estudiante":
        plan = PlanEstudio.query.get(body.plan_estudios_id)
        if not plan:
            return {"error": "El plan de estudios no existe"}, 400

    try:
        user_data = {
            "nombres": body.nombres,
            "apellidos": body.apellidos,
            "email": body.email,
            "password": body.password,
            "rol": body.rol,
            "dni": body.dni,
        }
        user = AuthService.register_user(user_data, commit=False)

        if body.rol == "estudiante":
            db.session.add(
                Estudiante(user_id=user.id, plan_estudios_id=body.plan_estudios_id)
            )
        elif body.rol == "docente":
            db.session.add(
                Docente(user_id=user.id, categoria=body.categoria or "auxiliar")
            )

        AuditService.log(
            accion="crear_usuario",
            recurso=f"user:{user.id}",
            detalle=(
                f"Usuario creado: {user.email} ({user.rol}) "
                f"por {g.current_user.email}"
            ),
            user=g.current_user,
        )
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Error al crear usuario")
        return {"error": f"No se pudo crear el usuario: {exc}"}, 400

    return _serialize_user(user), 201


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
