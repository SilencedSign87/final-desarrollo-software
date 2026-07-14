from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserIdPath(BaseModel):
    """Schema para identificar un usuario en la URL."""

    user_id: int


class RoleUpdate(BaseModel):
    """Schema para actualizar el perfil de acceso de un usuario."""

    rol: str = Field(..., pattern="^(estudiante|docente|administrador|direccion)$")


class AdminUserCreate(BaseModel):
    """Schema para que el administrador cree usuarios del sistema."""

    nombres: str = Field(..., min_length=1, max_length=100)
    apellidos: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    rol: str = Field(..., pattern="^(estudiante|docente|administrador|direccion)$")
    dni: str = Field(..., pattern=r"^\d{8}$", description="DNI (exactamente 8 dígitos)")
    plan_estudios_id: Optional[int] = Field(
        None, description="Obligatorio si el rol es estudiante"
    )
    categoria: Optional[str] = Field(
        "auxiliar",
        pattern="^(auxiliar|asociado|principal)$",
        description="Categoría docente (si el rol es docente)",
    )

    @model_validator(mode="after")
    def validar_perfil(self):
        if self.rol == "estudiante" and not self.plan_estudios_id:
            raise ValueError("Debes indicar el plan de estudios para un estudiante")
        return self


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
        pattern="^(login|login_fallido|logout|cambio_rol|crear_usuario|autorizar_documento|rechazar_documento|emitir_documento)$",
    )


class AuditoriaLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    usuario_email: Optional[str] = None
    accion: str
    recurso: Optional[str] = None
    detalle: str
    fecha_creacion: str
