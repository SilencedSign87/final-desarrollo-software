from typing import Optional

from pydantic import BaseModel, Field, RootModel


class TipoDocumentoPath(BaseModel):
    tipo_id: int = Field(..., description="ID del tipo de documento")


class TipoDocumentoCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    requiere_pago: bool = Field(False, description="Si el estudiante debe adjuntar comprobante")
    activo: bool = Field(True)


class TipoDocumentoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    requiere_pago: Optional[bool] = None
    activo: Optional[bool] = None


class TipoDocumentoResponse(BaseModel):
    id: int
    nombre: str
    requiere_pago: bool
    activo: bool


class TipoDocumentoListResponse(RootModel[list[TipoDocumentoResponse]]):
    pass
