from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class SolicitudDocumentoPath(BaseModel):
    """Schema para identificar una solicitud en la URL."""

    solicitud_id: int


class SolicitudDocumentoCreate(BaseModel):
    """Schema para solicitar certificados o constancias (JSON sin archivo)."""

    tipo_documento_id: Optional[int] = Field(None, description="ID del tipo de documento")
    tipo_documento: Optional[str] = Field(None, min_length=3, max_length=100)


class DocumentoEmitir(BaseModel):
    """Schema reservado para emision manual opcional."""

    archivo_url: Optional[str] = Field(default=None, min_length=5, max_length=255)
    qr_hash: Optional[str] = Field(default=None, min_length=5, max_length=255)


class QrVerificacionPath(BaseModel):
    """Schema para verificar un documento mediante su codigo QR."""

    qr_hash: str = Field(..., min_length=5, max_length=255)


class DocumentoVerificacionResponse(BaseModel):
    """Schema de respuesta para verificacion de documentos."""

    valido: bool
    solicitud_id: Optional[int] = None
    codigo_ticket: Optional[str] = None
    tipo_documento: Optional[str] = None
    estudiante: Optional[str] = None
    estado: Optional[str] = None
    fecha_emision: Optional[datetime] = None
    firma_valida: Optional[bool] = None
    mensaje: str


class DocumentoAutorizar(BaseModel):
    """Schema para autorizar o rechazar documentos oficiales."""

    aprobado: bool
    observacion: Optional[str] = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validar_observacion_rechazo(self):
        if not self.aprobado and not (self.observacion and self.observacion.strip()):
            raise ValueError("La observación es obligatoria al rechazar una solicitud")
        return self


class SolicitudDocumentoQuery(BaseModel):
    """Query params para listado paginado de solicitudes."""

    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)
    estado: Optional[str] = Field(
        default=None,
        pattern="^(pendiente_autorizacion|autorizado|rechazado|emitido)$",
    )


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int


class SolicitudDocumentoResponse(BaseModel):
    """Schema de respuesta para solicitudes de documento."""

    id: int
    codigo_ticket: Optional[str] = None
    estudiante_id: int
    tipo_documento_id: Optional[int] = None
    tipo_documento: str
    estado: str
    observacion: Optional[str] = None
    qr_hash: Optional[str] = None
    firma_digital: Optional[str] = None
    archivo_url: Optional[str] = None
    comprobante_url: Optional[str] = None
    requiere_pago: bool = False
    fecha_creacion: datetime
