from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Usuario
from app.utils.validators import validate_required_fields, validate_rut
from app.utils.security import hash_password

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios', methods=['POST'])
@jwt_required()
def crear_usuario():
    """
    Crear nuevo usuario (solo accesible para administradores)
    """
    try:
        current_user = get_jwt_identity()
        
        # Verificar que el usuario sea administrador
        if current_user['rol'] != 'admin':
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['rut', 'nombre', 'apellido', 'password', 'rol']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return jsonify({'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        # Validar formato de RUT
        if not validate_rut(data['rut']):
            return jsonify({'error': 'Formato de RUT inválido'}), 400
        
        # Verificar si el RUT ya existe
        usuario_existente = Usuario.get_by_rut(data['rut'])
        if usuario_existente:
            return jsonify({'error': 'Ya existe un usuario con este RUT'}), 400
        
        # Hashear la contraseña
        hashed_password = hash_password(data['password'])
        
        # Preparar datos del usuario
        user_data = {
            'rut': data['rut'],
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'contraseña_hash': hashed_password,
            'rol': data['rol'],
            'especialidad': data.get('especialidad')
        }
        
        # Crear usuario
        nuevo_usuario = Usuario.create(user_data)
        
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'usuario': {
                'id': nuevo_usuario['id'],
                'rut': nuevo_usuario['rut'],
                'nombre': nuevo_usuario['nombre'],
                'apellido': nuevo_usuario['apellido'],
                'rol': nuevo_usuario['rol'],
                'especialidad': nuevo_usuario['especialidad'],
                'activo': nuevo_usuario['activo'],
                'created_at': nuevo_usuario['created_at'].isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500

@usuarios_bp.route('/usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios():
    """
    Listar todos los usuarios (solo accesible para administradores)
    """
    try:
        current_user = get_jwt_identity()
        
        # Verificar que el usuario sea administrador
        if current_user['rol'] != 'admin':
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        # Obtener parámetros de filtro opcionales
        rol = request.args.get('rol')
        
        query = "SELECT id, rut, nombre, apellido, rol, especialidad, activo, created_at FROM usuarios WHERE 1=1"
        params = []
        
        if rol:
            query += " AND rol = %s"
            params.append(rol)
        
        query += " ORDER BY nombre, apellido"
        
        usuarios = Usuario.execute_custom_query(query, params, fetch=True)
        
        usuarios_list = []
        for usuario in usuarios:
            usuarios_list.append({
                'id': usuario['id'],
                'rut': usuario['rut'],
                'nombre': usuario['nombre'],
                'apellido': usuario['apellido'],
                'rol': usuario['rol'],
                'especialidad': usuario['especialidad'],
                'activo': usuario['activo'],
                'created_at': usuario['created_at'].isoformat() if usuario['created_at'] else None
            })
        
        return jsonify({
            'usuarios': usuarios_list,
            'total': len(usuarios_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al listar usuarios: {str(e)}'}), 500
    


@usuarios_bp.route('/usuarios/create-admin', methods=['POST'])
def crear_admin_inicial():
    """
    Endpoint para crear usuario admin inicial (sin requerir autenticación)
    Solo se debe usar una vez durante la instalación
    """
    try:
        # Verificar si ya existe un admin
        existing_admin = Usuario.execute_custom_query(
            "SELECT * FROM usuarios WHERE rol = 'admin' LIMIT 1", 
            fetch_one=True
        )
        
        if existing_admin:
            return jsonify({'error': 'Ya existe un usuario administrador en el sistema'}), 400
        
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['rut', 'nombre', 'apellido', 'password']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return jsonify({'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        # Validar formato de RUT
        if not validate_rut(data['rut']):
            return jsonify({'error': 'Formato de RUT inválido'}), 400
        
        # Verificar si el RUT ya existe
        usuario_existente = Usuario.get_by_rut(data['rut'])
        if usuario_existente:
            return jsonify({'error': 'Ya existe un usuario con este RUT'}), 400
        
        # Hashear la contraseña
        hashed_password = hash_password(data['password'])
        
        # Preparar datos del admin
        admin_data = {
            'rut': data['rut'],
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'contraseña_hash': hashed_password,
            'rol': 'admin',
            'especialidad': data.get('especialidad', 'Administración')
        }
        
        # Crear admin
        nuevo_admin = Usuario.create(admin_data)
        
        return jsonify({
            'message': 'Usuario administrador creado exitosamente',
            'usuario': {
                'id': nuevo_admin['id'],
                'rut': nuevo_admin['rut'],
                'nombre': nuevo_admin['nombre'],
                'apellido': nuevo_admin['apellido'],
                'rol': nuevo_admin['rol'],
                'especialidad': nuevo_admin['especialidad']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error al crear usuario administrador: {str(e)}'}), 500