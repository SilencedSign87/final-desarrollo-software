from flask import Blueprint, jsonify, request

from ..services.auth_service import AuthService


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # validación
    required = ['nombres', 'apellidos', 'rol', 'dni', 'email', 'password']
    if not all(field in data for field in required):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    from ..models.user import User
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El correo electrónico ya está registrado'}), 400
    
    user = AuthService.register_user(data)
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'user': {
            'id': user.id,
            'nombres': user.nombres,
            'apellidos': user.apellidos,
            'email': user.email,
            'rol': user.rol,
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # validación
    required = ['email', 'password']
    if not all(field in data for field in required):
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    user = AuthService.login(data)
    if not user:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    return jsonify({
        'message': 'Inicio de sesión exitoso',
        'user': {
            'id': user.id,
            'nombres': user.nombres,
            'apellidos': user.apellidos,
            'email': user.email,
            'rol': user.rol,
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    AuthService.logout()
    return jsonify({'message': 'Cierre de sesión exitoso'}), 200

@auth_bp.route('/current_user', methods=['GET'])
def current_user():
    user = AuthService.get_current_user()
    if not user:
        return jsonify({'error': 'No hay usuario autenticado'}), 401
    
    return jsonify({
        'user': {
            'id': user.id,
            'nombres': user.nombres,
            'apellidos': user.apellidos,
            'email': user.email,
            'rol': user.rol,
        }
    }), 200