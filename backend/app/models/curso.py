from ..extensions import db

curso_prerequisito = db.Table(
    "curso_prerequisito",
    db.Column(
        "curso_id",
        db.Integer,
        db.ForeignKey("curso.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "prerequisito_id",
        db.Integer,
        db.ForeignKey("curso.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)


class Curso(db.Model):
    __tablename__ = "curso"

    id = db.Column(db.Integer, primary_key=True)
    plan_estudios_id = db.Column(
        db.Integer,
        db.ForeignKey("plan_estudios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    nombre = db.Column(db.String(150), nullable=False)
    horas_teoria = db.Column(db.Integer, nullable=False)
    horas_practica = db.Column(db.Integer, nullable=False)
    semestre_num = db.Column(db.Integer, nullable=False)

    # Requisitos del curso
    prerequisitos = db.relationship(
        "Curso",
        secondary=curso_prerequisito,
        primaryjoin=(curso_prerequisito.c.curso_id == id),
        secondaryjoin=(curso_prerequisito.c.prerequisito_id == id),
        backref="cursos_que_lo_requieren",
        lazy="dynamic",
    )

    # Relationships
    secciones = db.relationship("Seccion", backref="curso", lazy=True)
