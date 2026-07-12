from ..extensions import db

class DetalleMatricula(db.Model):
    __tablename__ = 'detalle_matricula'

    id = db.Column(db.Integer, primary_key=True)
    matricula_id = db.Column(db.Integer, db.ForeignKey('matricula.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    seccion_id = db.Column(db.Integer, db.ForeignKey('seccion.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    estado_curso = db.Column(db.String(50), nullable=False)
    promedio_final = db.Column(db.Numeric(5, 2))
    is_validated = db.Column(db.Boolean, default=False)

    # Relationships
    evaluaciones = db.relationship('Evaluacion', backref='detalle_matricula', lazy=True)