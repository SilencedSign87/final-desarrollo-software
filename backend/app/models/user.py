from ..extensions import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(150), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # Relationships
    estudiante = db.relationship('Estudiante', backref='user', uselist=False)
    docente = db.relationship('Docente', backref='user', uselist=False)

