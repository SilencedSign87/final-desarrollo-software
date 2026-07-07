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
