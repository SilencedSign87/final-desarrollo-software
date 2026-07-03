from ..extensions import db

class Matricula(db.Model):
    __tablename__ = 'matricula'

    id = db.Column(db.Integer, primary_key=True)
    periodo_academico_id = db.Column(db.Integer, db.ForeignKey('periodo_academico.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    validado_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    observacion = db.Column(db.String(255))
    comprobante_url = db.Column(db.String(255))

    # Relationships
    detalles = db.relationship('DetalleMatricula', backref='matricula', lazy=True)
    validador = db.relationship('User', backref='matriculas_validadas', lazy=True)