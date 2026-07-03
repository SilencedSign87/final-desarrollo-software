from ..extensions import db

class PlanEstudio(db.Model):
    __tablename__ = 'plan_estudios'

    id = db.Column(db.Integer, primary_key=True)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidad.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    # Relationships
    cursos = db.relationship('Curso', backref='plan_estudio', lazy=True)
    estudiantes = db.relationship('Estudiante', backref='plan_estudio', lazy=True)