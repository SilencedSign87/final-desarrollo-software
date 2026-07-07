from flask_openapi3 import APIBlueprint, Tag

from ..extensions import db
from ..middleware import auth_required, roles_required
from ..models.solicitud_documento import SolicitudDocumento
from ..models.user import User
from ..schemas.generic_schema import ErrorResponse
from ..schemas.security_schema import AuditReportResponse, RoleUpdate
from ..schemas.user_schema import UserResponse

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
def update_user_role(user_id: int, body: RoleUpdate):
    """Definir o actualizar el perfil de acceso de un usuario."""
    user = User.query.get(user_id)
    if not user:
        return {"error": "Usuario no encontrado"}, 404

    user.rol = body.rol
    db.session.commit()

    return (
        _serialize_user(user),
        200,
    )


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
        ).model_dump(),
        200,
    )
