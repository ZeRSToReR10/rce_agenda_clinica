from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Usuario, CentroSalud, SesionTrabajo
from app.utils.security import create_jwt_token
from app.utils.validators import validate_rut
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['rut', 'password', 'centro_salud_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        # Validar formato de RUT
        if not validate_rut(data['rut']):
            return jsonify({'error': 'Formato de RUT inválido'}), 400
        
        # Verificar centro de salud
        centro_salud = CentroSalud.get_by_id(data['centro_salud_id'])
        if not centro_salud:
            return jsonify({'error': 'Centro de salud no válido'}), 400
        
        # Buscar usuario
        user = Usuario.get_by_rut(data['rut'])
        if not user:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not Usuario.verify_password(user['contraseña_hash'], data['password']):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Crear sesión de trabajo
        sesion = SesionTrabajo.create_sesion(
            user['id'], 
            data['centro_salud_id'], 
            datetime.now().date()
        )
        
        # Crear token JWT
        token = create_jwt_token(user)
        
        return jsonify({
            'message': 'Login exitoso',
            'token': token,
            'user': {
                'id': user['id'],
                'rut': user['rut'],
                'nombre': user['nombre'],
                'apellido': user['apellido'],
                'rol': user['rol'],
                'especialidad': user['especialidad']
            },
            'centro_salud': {
                'id': centro_salud['id'],
                'nombre': centro_salud['nombre']
            },
            'sesion': {
                'id': sesion['id'],
                'fecha': sesion['fecha'].isoformat(),
                'hora_inicio': str(sesion['hora_inicio']) if sesion['hora_inicio'] else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

@auth_bp.route('/centros', methods=['GET'])
def get_centros_salud():
    try:
        centros = CentroSalud.get_all()
        centros_list = [
            {
                'id': centro['id'],
                'nombre': centro['nombre'],
                'direccion': centro['direccion'],
                'telefono': centro['telefono']
            }
            for centro in centros
        ]
        return jsonify(centros_list), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener centros de salud: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Endpoint opcional para cerrar sesión de trabajo
    """
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        sesion_id = data.get('sesion_id')
        if sesion_id:
            # Aquí podrías implementar el cierre de sesión
            # SesionTrabajo.cerrar_sesion(sesion_id)
            pass
        
        return jsonify({'message': 'Logout exitoso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en logout: {str(e)}'}), 500