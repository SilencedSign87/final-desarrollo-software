from pydantic import BaseModel, Field, RootModel
from typing import Optional


class SeccionCreate(BaseModel):
    """Schema para que el admin cree una nueva sección (asigna docente a un curso)"""
    curso_id: int = Field(..., description="ID del curso")
    docente_id: int = Field(..., description="ID del docente asignado")
    periodo_academico_id: int = Field(..., description="ID del periodo académico")
    nombre: str = Field(..., min_length=1, max_length=100, description="Ej: 'DAW-A'")
    aforo: int = Field(..., gt=0, description="Cupos disponibles, debe ser mayor a 0")


class SeccionUpdate(BaseModel):
    """Schema para que el admin reasigne docente/aforo de una sección"""
    docente_id: Optional[int] = Field(None, description="Reasignar docente")
    aforo: Optional[int] = Field(None, gt=0)


class SilaboUpload(BaseModel):
    """Schema para cargar la URL del sílabo"""
    silabo_url: str = Field(..., min_length=1, description="URL/ruta del sílabo subido")


class SeccionResponse(BaseModel):
    id: int
    curso_id: int
    docente_id: int
    periodo_academico_id: int
    nombre: str
    aforo: int
    silabo_url: Optional[str] = None
    acta_validada: bool = False
    cupos_ocupados: int = 0


class SeccionListResponse(RootModel[list[SeccionResponse]]):
    """Wrapper para que flask_openapi3 acepte una lista de secciones como respuesta válida"""
    pass