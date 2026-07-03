from ..extensions import db

class Horario(db.Model):
    __tablename__ = 'horario'

    id = db.Column(db.Integer, primary_key=True)
    seccion_id = db.Column(db.Integer, db.ForeignKey('seccion.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_final = db.Column(db.Time, nullable=False)
    aula = db.Column(db.String(100), nullable=False)