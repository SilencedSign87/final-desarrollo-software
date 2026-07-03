from ..extensions import db

class Especialidad(db.Model):
    __tablename__ = 'especialidad'

    id = db.Column(db.Integer, primary_key=True)
    facultad_id = db.Column(db.Integer, db.ForeignKey('facultad.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    modalidad = db.Column(db.String(50), nullable=False)

    # Relationships
    planes_estudio = db.relationship('PlanEstudio', backref='especialidad', lazy=True)