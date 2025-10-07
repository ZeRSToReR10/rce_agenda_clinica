from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Agenda
from datetime import datetime, date
import re
from app.models.database import db

agendas_bp = Blueprint('agendas', __name__)

def validate_date_format(date_string):
    """Valida que la fecha esté en formato YYYY-MM-DD"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_string):
        return False
    
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@agendas_bp.route('/dia', methods=['GET'])
@jwt_required()
def get_agenda_dia():
    try:
        current_user = get_jwt_identity()
        usuario_id = current_user['id']
        
        # Obtener parámetros
        centro_salud_id = request.args.get('centro_salud_id')
        fecha_str = request.args.get('fecha', datetime.now().date().isoformat())
        
        if not centro_salud_id:
            return jsonify({'error': 'El parámetro centro_salud_id es requerido'}), 400
        
        # Convertir fecha
        try:
            fecha = date.fromisoformat(fecha_str.strip())
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        # Obtener agenda
        agendas = Agenda.get_daily_agenda(usuario_id, centro_salud_id, fecha)
        
        # Formatear respuesta
        agendas_list = []
        for agenda in agendas:
            agenda_dict = {
                'agenda_id': agenda['agenda_id'],
                'fecha': agenda['fecha'].isoformat(),
                'hora': str(agenda['hora']),
                'estado_agenda': agenda['estado_agenda'],
                'tipo_consulta': agenda['tipo_consulta'],
                'n_ficha': agenda['n_ficha'],
                'n_carpeta': agenda['n_carpeta'],
                'paciente': {
                    'rut': agenda['paciente_rut'],
                    'nombre': agenda['paciente_nombre'],
                    'apellido': agenda['paciente_apellido'],
                    'telefono': agenda['paciente_telefono'],
                    'edad': agenda['paciente_edad'],
                    'genero': agenda['paciente_genero']
                },
                'consulta': {
                    'estado_hora': agenda['estado_hora'],
                    'estado_atencion': agenda['estado_atencion'],
                    'modalidad_atencion': agenda['modalidad_atencion'],  # ¡NUEVO CAMPO!
                    'diagnostico': agenda['diagnostico']
                } if agenda['estado_hora'] else None  # Solo crear objeto consulta si existe
            }
            agendas_list.append(agenda_dict)
        
        return jsonify({
            'fecha': fecha.isoformat(),
            'agendas': agendas_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener agenda: {str(e)}'}), 500

@agendas_bp.route('/debug/<int:agenda_id>', methods=['GET'])
@jwt_required()
def debug_agenda(agenda_id):
    """
    Endpoint temporal para debug de agendas
    """
    try:
        current_user = get_jwt_identity()
        usuario_id = current_user['id']
        
        print(f"🔍 DEBUG - Usuario actual: {usuario_id}")
        print(f"🔍 DEBUG - Agenda solicitada: {agenda_id}")
        
        # Verificar si la agenda existe sin filtrar por usuario
        query_sin_filtro = """
        SELECT a.id, a.usuario_id, a.centro_salud_id, u.nombre as usuario_nombre
        FROM agendas a 
        JOIN usuarios u ON a.usuario_id = u.id 
        WHERE a.id = %s
        """
        agenda_sin_filtro = db.execute_query(query_sin_filtro, (agenda_id,), fetch_one=True)
        
        # Verificar con filtro de usuario
        query_con_filtro = """
        SELECT a.id, a.usuario_id, a.centro_salud_id, u.nombre as usuario_nombre
        FROM agendas a 
        JOIN usuarios u ON a.usuario_id = u.id 
        WHERE a.id = %s AND a.usuario_id = %s
        """
        agenda_con_filtro = db.execute_query(query_con_filtro, (agenda_id, usuario_id), fetch_one=True)
        
        return jsonify({
            'usuario_actual': current_user,
            'agenda_sin_filtro_usuario': agenda_sin_filtro,
            'agenda_con_filtro_usuario': agenda_con_filtro,
            'existe_agenda_sin_filtro': bool(agenda_sin_filtro),
            'existe_agenda_con_filtro': bool(agenda_con_filtro)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@agendas_bp.route('/<int:agenda_id>', methods=['GET'])
@jwt_required()
def get_detalle_agenda(agenda_id):
    try:
        current_user = get_jwt_identity()
        usuario_id = current_user['id']
        
        print(f"🔍 DEBUG - Buscando agenda {agenda_id} para usuario {usuario_id}")
        
        # Obtener detalle completo de la agenda
        agenda_detalle = Agenda.get_detalle_completo(agenda_id, usuario_id)
        
        print(f"🔍 DEBUG - Resultado de get_detalle_completo: {agenda_detalle}")
        print(f"🔍 DEBUG - Tipo del resultado: {type(agenda_detalle)}")
        
        if not agenda_detalle:
            print(f"❌ DEBUG - Agenda {agenda_id} no encontrada para usuario {usuario_id}")
            return jsonify({'error': 'Agenda no encontrada o no tienes permisos para acceder a ella'}), 404
        
        # Verificar que sea un diccionario
        if not isinstance(agenda_detalle, dict):
            print(f"❌ DEBUG - El resultado no es un diccionario: {type(agenda_detalle)}")
            return jsonify({'error': 'Error en el formato de datos'}), 500
        
        print(f"✅ DEBUG - Agenda encontrada: ID {agenda_detalle.get('agenda_id')}")
        
        # Formatear respuesta
        response_data = {
            'agenda': {
                'id': agenda_detalle['agenda_id'],
                'fecha': agenda_detalle['fecha'].isoformat() if agenda_detalle['fecha'] else None,
                'hora': str(agenda_detalle['hora']) if agenda_detalle['hora'] else None,
                'estado': agenda_detalle['estado_agenda'],
                'tipo_consulta': agenda_detalle['tipo_consulta'],
                'n_ficha': agenda_detalle['n_ficha'],
                'n_carpeta': agenda_detalle['n_carpeta'],
                'medico': {
                    'nombre': agenda_detalle['medico_nombre'],
                    'apellido': agenda_detalle['medico_apellido'],
                    'especialidad': agenda_detalle['medico_especialidad']
                },
                'centro_salud': {
                    'id': agenda_detalle['centro_salud_id'],
                    'nombre': agenda_detalle['centro_nombre']
                }
            },
            'paciente': {
                'id': agenda_detalle['paciente_id'],
                'rut': agenda_detalle['paciente_rut'],
                'nombre': agenda_detalle['paciente_nombre'],
                'apellido': agenda_detalle['paciente_apellido'],
                'telefono': agenda_detalle['paciente_telefono'],
                'edad': agenda_detalle['paciente_edad'],
                'genero': agenda_detalle['paciente_genero'],
                'direccion': agenda_detalle['paciente_direccion'],
                'fecha_nacimiento': agenda_detalle['paciente_fecha_nacimiento'].isoformat() if agenda_detalle['paciente_fecha_nacimiento'] else None,
                'email': agenda_detalle['paciente_email']
            }
        }
        
        # Agregar datos de consulta si existe
        if agenda_detalle['consulta_id']:
            response_data['consulta'] = {
                'id': agenda_detalle['consulta_id'],
                'estado_hora': agenda_detalle['estado_hora'],
                'estado_atencion': agenda_detalle['estado_atencion'],
                'modalidad_atencion': agenda_detalle['modalidad_atencion'],
                'actividad': agenda_detalle['actividad'],
                'tipo_alta': agenda_detalle['tipo_alta'],
                'diagnostico': agenda_detalle['diagnostico'],
                'observaciones': agenda_detalle['observaciones'],
                'ges': agenda_detalle['ges'],
                'ingreso_diag': agenda_detalle['ingreso_diag'],
                'control_tto': agenda_detalle['control_tto'],
                'egreso': agenda_detalle['egreso'],
                'pscv': agenda_detalle['pscv'],
                'morbilidad': agenda_detalle['morbilidad'],
                'psm': agenda_detalle['psm'],
                'cns': agenda_detalle['cns'],
                'lmp_lme': agenda_detalle['lmp_lme'],
                'consejeria_lm': agenda_detalle['consejeria_lm'],
                'embarazada': agenda_detalle['embarazada'],
                'visita_domic': agenda_detalle['visita_domic'],
                'dep_severa': agenda_detalle['dep_severa'],
                'remoto': agenda_detalle['remoto'],
                'created_at': agenda_detalle['consulta_created_at'].isoformat() if agenda_detalle['consulta_created_at'] else None,
                'updated_at': agenda_detalle['consulta_updated_at'].isoformat() if agenda_detalle['consulta_updated_at'] else None
            }
        
        return jsonify(response_data), 200
        
    except KeyError as e:
        print(f"❌ DEBUG - Error de clave faltante: {e}")
        return jsonify({'error': f'Campo faltante en los datos: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ DEBUG - Error general: {e}")
        return jsonify({'error': f'Error al obtener detalle de agenda: {str(e)}'}), 500
    

@agendas_bp.route('/<int:agenda_id>/estado', methods=['PUT'])
@jwt_required()
def actualizar_estado_agenda(agenda_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos requeridos
        if 'estado' not in data:
            return jsonify({'error': 'El campo estado es requerido'}), 400
        
        # Verificar que la agenda existe y pertenece al usuario
        agenda = Agenda.get_detalle_completo(agenda_id, current_user['id'])
        if not agenda:
            return jsonify({'error': 'Agenda no encontrada o no tienes permisos para acceder a ella'}), 404
        
        # Actualizar estado
        Agenda.update_status(agenda_id, data['estado'])
        
        return jsonify({
            'message': 'Estado de agenda actualizado exitosamente',
            'agenda_id': agenda_id,
            'nuevo_estado': data['estado']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al actualizar estado de agenda: {str(e)}'}), 500
