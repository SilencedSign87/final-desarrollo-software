from ..extensions import db

class Seccion(db.Model):
    __tablename__ = 'seccion'

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('docente.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    periodo_academico_id = db.Column(db.Integer, db.ForeignKey('periodo_academico.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    aforo = db.Column(db.Integer, nullable=False)
    silabo_url = db.Column(db.String(255))
    acta_validada = db.Column(db.Boolean, default=False)

    # Relationships
    horarios = db.relationship('Horario', backref='seccion', lazy=True)
    tipos_evaluacion = db.relationship('TipoEvaluacion', backref='seccion', lazy=True)
    detalles_matricula = db.relationship('DetalleMatricula', backref='seccion', lazy=True)