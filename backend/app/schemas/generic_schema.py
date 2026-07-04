from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Schema para respuesta de error"""
    message: str
    detail: str