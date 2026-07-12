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
    promedio_calculado: float | None = None
    is_validated: bool = False
    evaluaciones: list[EvaluacionSimpleResponse]

class NotasEstudianteListResponse(RootModel[list[CursoNotasResponse]]):
    pass


class RecordCursoResponse(BaseModel):
    nombre: str
    semestre_num: int
    prerequisitos: list[str]
    promedio: float | None = None


class RecordPeriodoResponse(BaseModel):
    periodo: str
    periodo_id: int
    cursos: list[RecordCursoResponse]


class RecordAcademicoResponse(RootModel[list[RecordPeriodoResponse]]):
    pass


class ResumenStats(BaseModel):
    total_estudiantes: int
    promedio_general: float | None = None
    aprobados: int
    aprobados_porcentaje: float | None = None
    desaprobados: int
    desaprobados_porcentaje: float | None = None
    distribucion: dict[str, int]


class DetalleStatsCurso(BaseModel):
    curso_id: int
    curso: str
    total_estudiantes: int
    promedio: float | None = None
    aprobados: int
    desaprobados: int


class DetalleStatsSeccion(BaseModel):
    seccion_id: int
    seccion: str
    curso: str
    docente: str
    total_estudiantes: int
    promedio: float | None = None
    aprobados: int
    desaprobados: int


class DetalleStatsEstudiante(BaseModel):
    estudiante_id: int
    estudiante: str
    promedio: float | None = None
    estado: str


class EstadisticasNotasResponse(BaseModel):
    periodo: str
    periodo_id: int
    resumen: ResumenStats
    detalle: list[DetalleStatsCurso | DetalleStatsSeccion | DetalleStatsEstudiante]


class RecordSeccionStats(BaseModel):
    seccion_id: int
    seccion: str
    docente: str
    total_estudiantes: int
    promedio: float | None = None
    aprobados: int
    desaprobados: int
    en_curso: int


class RecordCursoStats(BaseModel):
    curso_id: int
    curso: str
    semestre_num: int
    total_estudiantes: int
    promedio: float | None = None
    secciones: list[RecordSeccionStats]


class RecordAcademicoStatsResponse(BaseModel):
    periodo: str
    periodo_id: int
    cursos: list[RecordCursoStats]