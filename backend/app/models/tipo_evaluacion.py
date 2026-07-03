from ..extensions import db

class TipoEvaluacion(db.Model):
    __tablename__ = 'tipo_evaluacion'

    id = db.Column(db.Integer, primary_key=True)
    seccion_id = db.Column(db.Integer, db.ForeignKey('seccion.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    peso = db.Column(db.Numeric(5, 2), nullable=False)

    # Relationships
    evaluaciones = db.relationship('Evaluacion', backref='tipo_evaluacion', lazy=True)