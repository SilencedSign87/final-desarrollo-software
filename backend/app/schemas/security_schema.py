from typing import Optional

from pydantic import BaseModel, Field


class UserIdPath(BaseModel):
    """Schema para identificar un usuario en la URL."""

    user_id: int


class RoleUpdate(BaseModel):
    """Schema para actualizar el perfil de acceso de un usuario."""

    rol: str = Field(..., pattern="^(estudiante|docente|administrador|direccion)$")


class AuditReportResponse(BaseModel):
    """Schema base para reportes estrategicos y auditorias."""

    total_usuarios: int
    total_solicitudes_documento: int
    documentos_pendientes: int
    documentos_emitidos: int
    total_eventos_auditoria: int = 0
    cambios_rol: int = 0


class AuditoriaLogQuery(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(15, ge=1, le=50)
    accion: Optional[str] = Field(
        default=None,
        pattern="^(login|login_fallido|logout|cambio_rol|autorizar_documento|rechazar_documento|emitir_documento)$",
    )


class AuditoriaLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    usuario_email: Optional[str] = None
    accion: str
    recurso: Optional[str] = None
    detalle: str
    fecha_creacion: str
