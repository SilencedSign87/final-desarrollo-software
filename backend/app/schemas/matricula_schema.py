from pydantic import BaseModel, Field, RootModel
from typing import Optional


class MatriculaCreate(BaseModel):
    """Schema para que el estudiante solicite una matrícula (JSON sin archivo)."""
    periodo_academico_id: int = Field(..., description="ID del periodo académico")
    comprobante_url: Optional[str] = Field(
        None, description="URL externa del comprobante (alternativa al archivo)"
    )
    secciones_ids: list[int] = Field(..., min_length=1, description="IDs de las secciones")


class MatriculaValidar(BaseModel):
    """Schema para que el admin valide o rechace una matrícula"""
    estado: str = Field(..., pattern="^(validada|rechazada)$", description="Nuevo estado de la matrícula")
    observacion: Optional[str] = Field(None, max_length=255, description="Motivo u observación")


class DetalleMatriculaResponse(BaseModel):
    id: int
    seccion_id: int
    seccion_nombre: Optional[str] = None
    curso_nombre: Optional[str] = None
    estado_curso: str


class MatriculaResponse(BaseModel):
    """Schema de respuesta para una matrícula"""
    id: int
    periodo_academico_id: int
    periodo_semestre: Optional[str] = None
    periodo_requiere_pago: bool = False
    estudiante_id: int
    estudiante_nombre: Optional[str] = None
    estado: str
    observacion: Optional[str] = None
    comprobante_url: Optional[str] = None
    validado_user_id: Optional[int] = None
    validador_nombre: Optional[str] = None
    detalles: list[DetalleMatriculaResponse] = []


class MatriculaListResponse(RootModel[list[MatriculaResponse]]):
    """Wrapper para que flask_openapi3 acepte una lista de matrículas como respuesta válida"""
    pass
