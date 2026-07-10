from pydantic import BaseModel, Field, RootModel

from app.schemas.curso_schema import CursoResponse


class PeriodoAcademicoSearchRequest(BaseModel):
    """Schema para búsqueda de periodos académicos"""
    semestre: str | None = Field(None, description="Semestre del periodo académico")
    estado: str | None = Field(None, description="Estado del periodo académico")


class PeriodoAcademicoCreate(BaseModel):
    """Schema para crear un periodo académico"""
    semestre: str = Field(..., min_length=1, max_length=50, description="Semestre (ej. 2026-I)")
    fecha_inicio: str = Field(..., description="Fecha de inicio (YYYY-MM-DD)")
    fecha_fin: str = Field(..., description="Fecha de fin (YYYY-MM-DD)")
    estado: str = Field(..., min_length=1, max_length=50, description="Estado del periodo")
    requiere_pago: bool = Field(False, description="Si la matrícula exige comprobante de pago")


class PeriodoAcademicoUpdate(BaseModel):
    """Schema para actualizar un periodo académico (todos opcionales)"""
    semestre: str | None = Field(None, min_length=1, max_length=50)
    fecha_inicio: str | None = Field(None, description="Fecha de inicio (YYYY-MM-DD)")
    fecha_fin: str | None = Field(None, description="Fecha de fin (YYYY-MM-DD)")
    estado: str | None = Field(None, min_length=1, max_length=50)
    requiere_pago: bool | None = Field(None, description="Si la matrícula exige comprobante de pago")


class PeriodoAcademicoResponse(BaseModel):
    """Schema para respuesta de periodo académico"""
    id: int
    semestre: str
    fecha_inicio: str
    fecha_fin: str
    estado: str
    requiere_pago: bool = False


class PeriodoAcademicoListResponse(RootModel[list[PeriodoAcademicoResponse]]):
    """Wrapper para que flask_openapi3 acepte una lista de periodos académicos como respuesta válida"""
    pass


class CursosPorPeriodoResponse(RootModel[list[CursoResponse]]):
    """Schema para respuesta de cursos por periodo académico"""
    pass
