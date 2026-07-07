from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SolicitudDocumentoPath(BaseModel):
    """Schema para identificar una solicitud en la URL."""

    solicitud_id: int


class SolicitudDocumentoCreate(BaseModel):
    """Schema para solicitar certificados o constancias."""

    tipo_documento: str = Field(..., min_length=3, max_length=100)


class DocumentoEmitir(BaseModel):
    """Schema para registrar la emision de un documento."""

    archivo_url: str = Field(..., min_length=5, max_length=255)
    qr_hash: str = Field(..., min_length=5, max_length=255)


class DocumentoAutorizar(BaseModel):
    """Schema para autorizar o rechazar documentos oficiales."""

    aprobado: bool
    observacion: Optional[str] = Field(default=None, max_length=255)


class SolicitudDocumentoResponse(BaseModel):
    """Schema de respuesta para solicitudes de documento."""

    id: int
    estudiante_id: int
    tipo_documento: str
    estado: str
    qr_hash: Optional[str] = None
    archivo_url: Optional[str] = None
    fecha_creacion: datetime
