from .extensions import db
from .models.user import User
from werkzeug.security import generate_password_hash


def seed_default_users():
    if User.query.first() is not None:
        return  # Ya hay usuarios

    default_users = [
        {
            "nombres": "Admin",
            "apellidos": "Sistema",
            "rol": "administrador",
            "dni": "00000000",
            "email": "admin@sistema.edu",
            "password": generate_password_hash("admin123"),
        },
        {
            "nombres": "Director",
            "apellidos": "Academico",
            "rol": "direccion",
            "dni": "11111111",
            "email": "director@sistema.edu",
            "password": generate_password_hash("director123"),
        },
        {
            "nombres": "Docente",
            "apellidos": "Ejemplo",
            "rol": "docente",
            "dni": "22222222",
            "email": "docente@sistema.edu",
            "password": generate_password_hash("docente123"),
        },
        {
            "nombres": "Estudiante",
            "apellidos": "Ejemplo",
            "rol": "estudiante",
            "dni": "33333333",
            "email": "estudiante@sistema.edu",
            "password": generate_password_hash("estudiante123"),
        },
    ]

    for user_data in default_users:
        user = User(**user_data)
        try:
            db.session.add(user)
        except Exception as e:
            print(f"[ERROR] Error al agregar usuario: {e}")
            continue

    db.session.commit()
    print("[SYSTEM] Usuarios por defecto creados exitosamente.")
