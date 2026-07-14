from ..extensions import db
from ..utils.datetime_utils import utc_now_naive


class AuditoriaLog(db.Model):
    """Bitácora append-only de acciones críticas del sistema."""

    __tablename__ = "auditoria_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    usuario_email = db.Column(db.String(150))
    accion = db.Column(db.String(50), nullable=False, index=True)
    recurso = db.Column(db.String(100))
    detalle = db.Column(db.String(500), nullable=False)
    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now_naive,
        index=True,
    )

    user = db.relationship("User", lazy=True)
