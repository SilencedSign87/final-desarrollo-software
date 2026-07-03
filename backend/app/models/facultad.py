from ..extensions import db

class Facultad(db.Model):
    __tablename__ = 'facultad'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    # Relationships
    especialidades = db.relationship('Especialidad', backref='facultad', lazy=True)

