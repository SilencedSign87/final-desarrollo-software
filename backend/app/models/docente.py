from ..extensions import db


class Docente(db.Model):
    __tablename__ = "docente"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    categoria = db.Column(db.String(100), nullable=False)

    # Relationships
    secciones = db.relationship("Seccion", backref="docente", lazy=True)
