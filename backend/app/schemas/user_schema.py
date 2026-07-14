from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """Schema para crear un usuario"""
    nombres: str = Field(..., min_length=1, max_length=100, description="Nombres del usuario")
    apellidos: str = Field(..., min_length=1, max_length=100, description="Apellidos del usuario")
    email: EmailStr
    password: str = Field(..., min_length=6, description="Contraseña (mín. 6 caracteres)")
    rol: str = Field(..., pattern="^(estudiante|docente|administrador|direccion)$", description="Rol del usuario")
    dni: str = Field(
        ...,
        pattern=r"^\d{8}$",
        description="DNI del usuario (exactamente 8 dígitos)",
    )

class UserLogin(BaseModel):
    """Schema para iniciar sesión"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema para respuesta de usuario (sin password)"""
    id: int
    nombres: str
    apellidos: str
    email: str
    rol: str
    
class UserCurrent(BaseModel):
    """Schema para el usuario actual"""
    id: int
    nombres: str
    apellidos: str
    email: str
    rol: str