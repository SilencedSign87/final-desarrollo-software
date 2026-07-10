from pydantic import BaseModel, Field, RootModel
from typing import Optional
from decimal import Decimal


class EvaluacionCreate(BaseModel):
    tipo_evaluacion_id: int = Field(..., description="ID del tipo de evaluación")
    detalle_matricula_id: int = Field(..., description="ID del detalle de matrícula")
    nota: Decimal = Field(..., description="Nota obtenida")


class EvaluacionUpdate(BaseModel):
    nota: Optional[Decimal] = Field(None, description="Nota obtenida")


class EvaluacionResponse(BaseModel):
    id: int
    tipo_evaluacion_id: int
    detalle_matricula_id: int
    nota: Decimal


class EvaluacionListResponse(RootModel[list[EvaluacionResponse]]):
    pass


class TipoEvaluacionCreate(BaseModel):
    seccion_id: int = Field(..., description="ID de la sección")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del tipo de evaluación")
    peso: Decimal = Field(..., description="Peso porcentual del tipo de evaluación")


class TipoEvaluacionUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=100, description="Nombre del tipo de evaluación")
    peso: Decimal | None = Field(None, description="Peso porcentual del tipo de evaluación")


class TipoEvaluacionResponse(BaseModel):
    id: int
    seccion_id: int
    nombre: str
    peso: Decimal


class TipoEvaluacionListResponse(RootModel[list[TipoEvaluacionResponse]]):
    pass


class EstudianteSimpleResponse(BaseModel):
    id: int
    user_id: int
    plan_estudios_id: int


class TipoEvaluacionListResponse(RootModel[list[TipoEvaluacionResponse]]):
    pass

class NotaPorTipoEvaluacion(BaseModel):
    tipo_evaluacion_id: int
    evaluacion_id: int | None = None
    nota: Decimal | None = None


class EstudianteConNotasResponse(BaseModel):
    detalle_matricula_id: int
    estudiante_id: int
    estudiante_nombre: str
    notas: list[NotaPorTipoEvaluacion]
    promedio_final: Decimal | None = None


class NotasSeccionResponse(BaseModel):
    tipos_evaluacion: list[TipoEvaluacionResponse]
    estudiantes: list[EstudianteConNotasResponse]

class EvaluacionSimpleResponse(BaseModel):
    nombre: str
    nota: Decimal
    peso: Decimal


class CursoNotasResponse(BaseModel):
    curso: str
    seccion: str
    promedio: Decimal | None = None
    evaluaciones: list[EvaluacionSimpleResponse]

class NotasEstudianteListResponse(RootModel[list[CursoNotasResponse]]):
    pass