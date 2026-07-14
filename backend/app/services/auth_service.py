from ..extensions import db
from ..models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session


class AuthService:
    @staticmethod
    def register_user(data, commit=True):
        hashed = generate_password_hash(data["password"])
        user = User(
            nombres=data["nombres"],
            apellidos=data["apellidos"],
            rol=data["rol"],
            dni=data["dni"],
            email=data["email"],
            password=hashed,
        )
        db.session.add(user)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return user
    
    @staticmethod
    def login(data):
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not check_password_hash(user.password, data["password"]):
            return None
        
        session['user_id'] = user.id
        session['rol'] = user.rol
        session.permanent = True

        return user
    
    @staticmethod
    def logout():
        session.clear()

    @staticmethod
    def get_current_user():
        user_id = session.get('user_id')
        if not user_id:
            return None
        return User.query.get(user_id)
