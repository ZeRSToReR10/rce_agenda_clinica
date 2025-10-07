from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Paciente
from app.models.database import db
from app.utils.validators import validate_required_fields, validate_rut

pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/buscar', methods=['GET'])
@jwt_required()
def buscar_paciente():
    try:
        rut = request.args.get('rut', '')
        
        if not rut:
            return jsonify({'error': 'El parámetro RUT es requerido'}), 400
        
        # Limpiar RUT (remover puntos y guión)
        rut_limpio = rut.replace('.', '').replace('-', '')
        
        print(f"🔍 DEBUG - Buscando paciente con RUT: {rut} (limpio: {rut_limpio})")
        
        # Buscar paciente por RUT (limpio o con formato)
        query = """
        SELECT * FROM pacientes 
        WHERE REPLACE(REPLACE(rut, '.', ''), '-', '') = %s 
        """
        paciente = db.execute_query(query, (rut_limpio,), fetch_one=True)
        
        pacientes_list = []
        if paciente:
            pacientes_list = [paciente]
            print(f"✅ DEBUG - Paciente encontrado: {paciente['nombre']} {paciente['apellido']}")
        else:
            print(f"❌ DEBUG - No se encontró paciente con RUT: {rut}")
        
        # Formatear respuesta
        pacientes_formateados = []
        for paciente in pacientes_list:
            pacientes_formateados.append({
                'id': paciente['id'],
                'rut': paciente['rut'],
                'nombre': paciente['nombre'],
                'apellido': paciente['apellido'],
                'telefono': paciente['telefono'],
                'edad': paciente['edad'],
                'genero': paciente['genero'],
                'direccion': paciente['direccion']
            })
        
        return jsonify({
            'pacientes': pacientes_formateados,
            'total': len(pacientes_formateados)
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en buscar_paciente: {str(e)}")
        return jsonify({'error': f'Error al buscar paciente: {str(e)}'}), 500


@pacientes_bp.route('/', methods=['POST'])
@jwt_required()
def crear_paciente():
    try:
        data = request.get_json()
        
        print(f"🔍 DEBUG - Datos recibidos para crear paciente: {data}")
        
        # Validar campos requeridos
        required_fields = ['rut', 'nombre', 'apellido']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return jsonify({'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        # Validar formato de RUT
        if not validate_rut(data['rut']):
            return jsonify({'error': 'Formato de RUT inválido'}), 400
        
        # Verificar si el paciente ya existe
        paciente_existente = Paciente.get_by_rut(data['rut'])
        if paciente_existente:
            return jsonify({'error': 'Ya existe un paciente con este RUT'}), 400
        
        # Crear paciente con todos los campos
        nuevo_paciente = Paciente.create({
            'rut': data['rut'],
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'telefono': data.get('telefono'),
            'edad': data.get('edad'),
            'genero': data.get('genero'),
            'direccion': data.get('direccion'),
            'fecha_nacimiento': data.get('fecha_nacimiento'),
            'email': data.get('email')
        })
        
        if not nuevo_paciente:
            return jsonify({'error': 'No se pudo crear el paciente'}), 500
        
        print(f"✅ DEBUG - Paciente creado exitosamente: {nuevo_paciente}")
        
        return jsonify({
            'message': 'Paciente creado exitosamente',
            'paciente': {
                'id': nuevo_paciente['id'],
                'rut': nuevo_paciente['rut'],
                'nombre': nuevo_paciente['nombre'],
                'apellido': nuevo_paciente['apellido'],
                'telefono': nuevo_paciente['telefono'],
                'edad': nuevo_paciente['edad'],
                'genero': nuevo_paciente['genero'],
                'direccion': nuevo_paciente['direccion'],
                'fecha_nacimiento': nuevo_paciente['fecha_nacimiento'].isoformat() if nuevo_paciente['fecha_nacimiento'] else None,
                'email': nuevo_paciente['email']
            }
        }), 201
        
    except Exception as e:
        print(f"❌ ERROR en crear_paciente: {str(e)}")
        return jsonify({'error': f'Error al crear paciente: {str(e)}'}), 500