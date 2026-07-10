from ..extensions import db

class PeriodoAcademico(db.Model):
    __tablename__ = 'periodo_academico'

    id = db.Column(db.Integer, primary_key=True)
    semestre = db.Column(db.String(50), nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    requiere_pago = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    secciones = db.relationship('Seccion', backref='periodo_academico', lazy=True)
    matriculas = db.relationship('Matricula', backref='periodo_academico', lazy=True)