from ..extensions import db


class TipoDocumento(db.Model):
    __tablename__ = "tipo_documento"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    requiere_pago = db.Column(db.Boolean, nullable=False, default=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    solicitudes = db.relationship("SolicitudDocumento", backref="tipo", lazy=True)
