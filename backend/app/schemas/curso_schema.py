from pydantic import BaseModel, Field, RootModel
from typing import Optional


class CursoCreate(BaseModel):
    """Schema para que el admin cree un nuevo curso"""
    plan_estudios_id: int = Field(..., description="ID del plan de estudios al que pertenece")
    nombre: str = Field(..., min_length=1, max_length=150)
    horas_teoria: int = Field(..., ge=0, description="Horas de teoría semanales")
    horas_practica: int = Field(..., ge=0, description="Horas de práctica semanales")
    semestre_num: int = Field(..., ge=1, le=12, description="Semestre al que pertenece (1-12)")
    prerequisitos_ids: list[int] = Field(default=[], description="IDs de cursos prerequisito")


class CursoUpdate(BaseModel):
    """Schema para editar un curso existente (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    horas_teoria: Optional[int] = Field(None, ge=0)
    horas_practica: Optional[int] = Field(None, ge=0)
    semestre_num: Optional[int] = Field(None, ge=1, le=12)


class CursoResponse(BaseModel):
    id: int
    plan_estudios_id: int
    nombre: str
    horas_teoria: int
    horas_practica: int
    semestre_num: int
    prerequisitos_ids: list[int] = []


class CursoListResponse(RootModel[list[CursoResponse]]):
    """Wrapper para que flask_openapi3 acepte una lista de cursos como respuesta válida"""
    pass


class CursosDisponiblesResponse(BaseModel):
    """Respuesta de /cursos/disponibles: cursos que le tocan al estudiante en su semestre actual"""
    semestre_actual: int
    cursos: list[CursoResponse]