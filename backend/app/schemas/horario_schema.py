from pydantic import BaseModel, Field, RootModel, field_validator
from datetime import time
from typing import Optional


class HorarioCreate(BaseModel):
    """Schema para que el admin cree un horario para una sección"""
    seccion_id: int = Field(..., description="ID de la sección")
    dia_semana: int = Field(..., ge=0, le=6, description="0=lunes, 1=martes, ..., 6=domingo")
    hora_inicio: time = Field(..., description="Hora de inicio, formato HH:MM")
    hora_final: time = Field(..., description="Hora de fin, formato HH:MM")
    aula: str = Field(..., min_length=1, max_length=100)

    @field_validator("hora_final")
    @classmethod
    def hora_final_debe_ser_mayor(cls, v, info):
        hora_inicio = info.data.get("hora_inicio")
        if hora_inicio is not None and v <= hora_inicio:
            raise ValueError("hora_final debe ser posterior a hora_inicio")
        return v


class HorarioUpdate(BaseModel):
    dia_semana: Optional[int] = Field(None, ge=0, le=6)
    hora_inicio: Optional[time] = Field(None)
    hora_final: Optional[time] = Field(None)
    aula: Optional[str] = Field(None, min_length=1, max_length=100)


class HorarioResponse(BaseModel):
    id: int
    seccion_id: int
    dia_semana: int
    hora_inicio: time
    hora_final: time
    aula: str


class HorarioListResponse(RootModel[list[HorarioResponse]]):
    """Wrapper para que flask_openapi3 acepte una lista de horarios como respuesta válida"""
    pass