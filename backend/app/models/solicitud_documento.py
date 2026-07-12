from datetime import datetime, timezone

from ..extensions import db


class SolicitudDocumento(db.Model):
    __tablename__ = "solicitud_documento"

    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(
        db.Integer,
        db.ForeignKey("estudiante.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    tipo_documento_id = db.Column(
        db.Integer,
        db.ForeignKey("tipo_documento.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    tipo_documento = db.Column(db.String(100), nullable=False)
    codigo_ticket = db.Column(db.String(30), unique=True, nullable=True)
    estado = db.Column(db.String(50), nullable=False)
    observacion = db.Column(db.String(255))
    qr_hash = db.Column(db.String(255))
    firma_digital = db.Column(db.Text)
    firma_algoritmo = db.Column(db.String(50))
    firma_huella_cert = db.Column(db.String(64))
    contenido_hash = db.Column(db.String(128))
    archivo_url = db.Column(db.String(255))
    comprobante_url = db.Column(db.String(255))
    requiere_pago = db.Column(db.Boolean, nullable=False, default=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    fecha_emision = db.Column(db.DateTime)
    fecha_respuesta = db.Column(db.DateTime)
    respondido_por_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
