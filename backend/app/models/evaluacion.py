from ..extensions import db

class Evaluacion(db.Model):
    __tablename__ = 'evaluacion'

    id = db.Column(db.Integer, primary_key=True)
    tipo_evaluacion_id = db.Column(db.Integer, db.ForeignKey('tipo_evaluacion.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    detalle_matricula_id = db.Column(db.Integer, db.ForeignKey('detalle_matricula.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    nota = db.Column(db.Numeric(5, 2), nullable=False)