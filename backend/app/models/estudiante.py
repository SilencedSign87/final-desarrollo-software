from ..extensions import db


class Estudiante(db.Model):
    __tablename__ = "estudiante"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    plan_estudios_id = db.Column(
        db.Integer,
        db.ForeignKey("plan_estudios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    
    # Relationships
    matriculas = db.relationship("Matricula", backref="estudiante", lazy=True)
    solicitudes_documento = db.relationship('SolicitudDocumento', backref='estudiante', lazy=True)
