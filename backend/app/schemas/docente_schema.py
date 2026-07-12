from pydantic import BaseModel, Field, RootModel
from typing import Optional

class DocenteCreate(BaseModel):
    """Schema para que el admin cree el perfil de docente de un usuario ya registrado"""
    user_id: int = Field(..., description="ID del usuario (debe tener rol 'docente')")
    categoria: str = Field(..., min_length=1, max_length=100, description="Ej: auxiliar, asociado, principal")

class DocenteUpdate(BaseModel):
    categoria: Optional[str] = Field(None, min_length=1, max_length=100)

class SeccionAsignadaResponse(BaseModel):
    id: int
    curso_id: int
    curso_nombre: str
    nombre: str
    periodo_academico_id: int
    aforo: int
    silabo_url: Optional[str] = None

class DocenteResponse(BaseModel):
    id: int
    user_id: int
    categoria: str
    total_secciones: int = 0

class DocenteListResponse(RootModel[list[DocenteResponse]]):
    """Wrapper para que flask_openapi3 acepte una lista de docentes como respuesta válida"""
    pass

class SeccionesDocenteListResponse(RootModel[list[SeccionAsignadaResponse]]):
    """Wrapper para la lista de secciones asignadas a un docente"""
    pass