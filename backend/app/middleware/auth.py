from functools import wraps

from flask import g, session

from ..models.user import User


def auth_required(view):
    """Valida que exista una sesion activa antes de ejecutar la ruta."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Autenticacion requerida"}, 401

        user = User.query.get(user_id)
        if not user:
            session.clear()
            return {"error": "Sesion invalida"}, 401

        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def roles_required(*allowed_roles):
    """Permite el acceso solo a usuarios con alguno de los roles indicados."""

    def decorator(view):
        @wraps(view)
        @auth_required
        def wrapped(*args, **kwargs):
            user = g.current_user
            if user.rol not in allowed_roles:
                return {"error": "No tienes permisos para acceder a este recurso"}, 403

            return view(*args, **kwargs)

        return wrapped

    return decorator
