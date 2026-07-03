from ..extensions import db
from datetime import datetime, timezone

class SolicitudDocumento(db.Model):
    __tablename__ = 'solicitud_documento'

    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    tipo_documento = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    qr_hash = db.Column(db.String(255))
    archivo_url = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime, nullable=False)