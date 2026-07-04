from flask import Blueprint, jsonify, request
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, UserCurrent
from app.schemas.generic_schema import ErrorResponse
from ..services.auth_service import AuthService

auth_tag = Tag(
    name="Autenticación", description="Endpoints de registro, login y sesión"
)

auth_bp = APIBlueprint("auth", __name__, abp_tags=[auth_tag])


@auth_bp.post(
    "/register",
    responses={"201": UserResponse, "400": ErrorResponse},
)
def register(body: UserCreate):
    """Registrar un nuevo usuario"""
    from ..models.user import User

    if User.query.filter_by(email=body.email).first():
        return {"error": "El correo electrónico ya está registrado"}, 400
    user = AuthService.register_user(body.model_dump())
    return (
        UserResponse(
            id=user.id,
            nombres=user.nombres,
            apellidos=user.apellidos,
            email=user.email,
            rol=user.rol,
        ).model_dump(),
        201,
    )


@auth_bp.post(
    "/login",
    responses={
        "200": UserResponse,
          "401": ErrorResponse
          },
)
def login(body: UserLogin):
    """Iniciar sesión"""
    user = AuthService.login(body.model_dump())
    if not user:
        return {"error": "Credenciales inválidas"}, 401
    return (
        UserResponse(
            id=user.id,
            nombres=user.nombres,
            apellidos=user.apellidos,
            email=user.email,
            rol=user.rol,
        ).model_dump(),
        200,
    )


@auth_bp.post(
    "/logout",
    responses={
        "200": {
            "description": "Cierre de sesión exitoso",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        },
    },
)
def logout():
    """Cerrar sesión"""
    AuthService.logout()
    return {"message": "Cierre de sesión exitoso"}, 200


@auth_bp.get(
    "/current_user",
    responses={
        "200": UserResponse,
        "401": ErrorResponse,
    },
)
def current_user():
    """Obtener usuario autenticado actual"""
    user = AuthService.get_current_user()
    if not user:
        return {"error": "No hay usuario autenticado"}, 401
    return (
        UserResponse(
            id=user.id,
            nombres=user.nombres,
            apellidos=user.apellidos,
            email=user.email,
            rol=user.rol,
        ).model_dump(),
        200,
    )
