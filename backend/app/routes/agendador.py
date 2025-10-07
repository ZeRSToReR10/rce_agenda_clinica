from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Agenda, Usuario, Paciente, CentroSalud
from app.utils.validators import validate_required_fields, validate_rut
from datetime import datetime, date, time
import json
from app.models.database import db

agendador_bp = Blueprint('agendador', __name__)

@agendador_bp.route('/agendas', methods=['GET'])
@jwt_required()
def get_agendas():
    """
    Obtener agendas con filtros para agendador
    Puede filtrar por médico, centro, fecha, estado
    """
    try:
        current_user = get_jwt_identity()
        
        # Verificar que el usuario sea agendador
        if current_user['rol'] != 'scheduler':
            return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
        
        # Obtener parámetros de filtro
        usuario_id = request.args.get('usuario_id')
        centro_salud_id = request.args.get('centro_salud_id')
        fecha_str = request.args.get('fecha')
        estado = request.args.get('estado')
        
        # Construir query base
        query = """
        SELECT 
            a.id,
            a.fecha,
            a.hora,
            a.estado,
            a.tipo_consulta,
            a.n_ficha,
            a.n_carpeta,
            p.id as paciente_id,
            p.rut as paciente_rut,
            p.nombre as paciente_nombre,
            p.apellido as paciente_apellido,
            p.telefono as paciente_telefono,
            u.id as medico_id,
            u.nombre as medico_nombre,
            u.apellido as medico_apellido,
            u.especialidad as medico_especialidad,
            cs.nombre as centro_nombre
        FROM agendas a
        JOIN pacientes p ON a.paciente_id = p.id
        JOIN usuarios u ON a.usuario_id = u.id
        JOIN centros_salud cs ON a.centro_salud_id = cs.id
        WHERE 1=1
        """
        params = []
        
        # Aplicar filtros
        if usuario_id:
            query += " AND a.usuario_id = %s"
            params.append(usuario_id)
        
        if centro_salud_id:
            query += " AND a.centro_salud_id = %s"
            params.append(centro_salud_id)
        
        if fecha_str:
            try:
                fecha = date.fromisoformat(fecha_str)
                query += " AND a.fecha = %s"
                params.append(fecha)
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        if estado:
            query += " AND a.estado = %s"
            params.append(estado)
        
        query += " ORDER BY a.fecha DESC, a.hora DESC"
        
        # Ejecutar consulta
        agendas = Agenda.execute_custom_query(query, params, fetch=True)
        
        # Formatear respuesta
        agendas_list = []
        for agenda in agendas:
            agenda_data = {
                'id': agenda['id'],
                'fecha': agenda['fecha'].isoformat(),
                'hora': str(agenda['hora']),
                'estado': agenda['estado'],
                'tipo_consulta': agenda['tipo_consulta'],
                'n_ficha': agenda['n_ficha'],
                'n_carpeta': agenda['n_carpeta'],
                'paciente': {
                    'id': agenda['paciente_id'],
                    'rut': agenda['paciente_rut'],
                    'nombre': agenda['paciente_nombre'],
                    'apellido': agenda['paciente_apellido'],
                    'telefono': agenda['paciente_telefono']
                },
                'medico': {
                    'id': agenda['medico_id'],
                    'nombre': agenda['medico_nombre'],
                    'apellido': agenda['medico_apellido'],
                    'especialidad': agenda['medico_especialidad']
                },
                'centro_salud': agenda['centro_nombre']
            }
            agendas_list.append(agenda_data)
        
        return jsonify({
            'agendas': agendas_list,
            'total': len(agendas_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener agendas: {str(e)}'}), 500

@agendador_bp.route('/agendas', methods=['POST'])
@jwt_required()
def crear_agenda():
    try:
        current_user = get_jwt_identity()
        
        print(f"🔍 DEBUG crear_agenda - Usuario actual: {current_user}")
        
        # Verificar que el usuario sea agendador
        if current_user['rol'] != 'scheduler':
            return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
        
        data = request.get_json()
        
        print(f"🔍 DEBUG crear_agenda - Datos recibidos: {data}")
        
        # Validar campos requeridos
        required_fields = ['paciente_id', 'usuario_id', 'centro_salud_id', 'fecha', 'hora']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            print(f"❌ DEBUG crear_agenda - Campos faltantes: {missing_fields}")
            return jsonify({'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        # Verificar que el paciente existe
        paciente = Paciente.get_by_id(data['paciente_id'])
        if not paciente:
            print(f"❌ DEBUG crear_agenda - Paciente no encontrado: {data['paciente_id']}")
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        print(f"✅ DEBUG crear_agenda - Paciente encontrado: {paciente['nombre']} {paciente['apellido']}")
        
        # Verificar que el médico existe y es health-worker
        medico = Usuario.get_by_id(data['usuario_id'])
        if not medico or medico['rol'] != 'health-worker':
            print(f"❌ DEBUG crear_agenda - Médico no válido: {data['usuario_id']}")
            return jsonify({'error': 'Médico no válido'}), 400
        
        print(f"✅ DEBUG crear_agenda - Médico válido: {medico['nombre']} {medico['apellido']}")
        
        # Verificar que el centro de salud existe
        centro_salud = CentroSalud.get_by_id(data['centro_salud_id'])
        if not centro_salud:
            print(f"❌ DEBUG crear_agenda - Centro de salud no válido: {data['centro_salud_id']}")
            return jsonify({'error': 'Centro de salud no válido'}), 400
        
        print(f"✅ DEBUG crear_agenda - Centro de salud válido: {centro_salud['nombre']}")
        
        # Verificar formato de fecha
        try:
            fecha = date.fromisoformat(data['fecha'])
        except ValueError:
            print(f"❌ DEBUG crear_agenda - Formato de fecha inválido: {data['fecha']}")
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        # Verificar que la fecha no sea en el pasado
        if fecha < datetime.now().date():
            print(f"❌ DEBUG crear_agenda - Fecha en el pasado: {fecha}")
            return jsonify({'error': 'No se pueden crear agendas en fechas pasadas'}), 400
        
        # Verificar formato de hora
        try:
            hora = time.fromisoformat(data['hora'])
        except ValueError:
            print(f"❌ DEBUG crear_agenda - Formato de hora inválido: {data['hora']}")
            return jsonify({'error': 'Formato de hora inválido. Use HH:MM:SS'}), 400
        
        # Verificar si ya existe una agenda en ese horario
        agenda_existente = Agenda.get_agenda_por_horario(
            data['usuario_id'], 
            data['fecha'], 
            data['hora']
        )
        
        if agenda_existente:
            print(f"❌ DEBUG crear_agenda - Horario ocupado: {data['usuario_id']}, {data['fecha']}, {data['hora']}")
            return jsonify({'error': 'Ya existe una agenda para ese médico en ese horario'}), 400
        
        # Crear la nueva agenda
        nueva_agenda = Agenda.crear_agenda(
            paciente_id=data['paciente_id'],
            usuario_id=data['usuario_id'],
            centro_salud_id=data['centro_salud_id'],
            fecha=data['fecha'],
            hora=data['hora'],
            tipo_consulta=data.get('tipo_consulta', 'consulta'),
            n_ficha=data.get('n_ficha'),
            n_carpeta=data.get('n_carpeta')
        )
        
        print(f"✅ DEBUG crear_agenda - Agenda creada exitosamente: {nueva_agenda['id']}")
        
        return jsonify({
            'message': 'Agenda creada exitosamente',
            'agenda_id': nueva_agenda['id'],
            'agenda': {
                'id': nueva_agenda['id'],
                'fecha': nueva_agenda['fecha'].isoformat(),
                'hora': str(nueva_agenda['hora']),
                'estado': nueva_agenda['estado'],
                'tipo_consulta': nueva_agenda['tipo_consulta']
            }
        }), 201
        
    except Exception as e:
        print(f"❌ ERROR en crear_agenda: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        return jsonify({'error': f'Error al crear agenda: {str(e)}'}), 500
    
    
@agendador_bp.route('/agendas/<int:agenda_id>', methods=['PUT'])
@jwt_required()
def actualizar_agenda(agenda_id):
    """
    Actualizar agenda existente
    """
    try:
        current_user = get_jwt_identity()
        
        if current_user['rol'] != 'scheduler':
            return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
        
        data = request.get_json()
        
        # Verificar que la agenda existe
        agenda = Agenda.get_by_id(agenda_id)
        if not agenda:
            return jsonify({'error': 'Agenda no encontrada'}), 404
        
        # Campos permitidos para actualización
        campos_permitidos = {
            'paciente_id', 'usuario_id', 'centro_salud_id', 'fecha', 'hora',
            'tipo_consulta', 'n_ficha', 'n_carpeta', 'estado'
        }
        
        update_data = {}
        for campo, valor in data.items():
            if campo in campos_permitidos:
                update_data[campo] = valor
        
        # Si se cambia fecha/hora/médico, verificar disponibilidad
        if any(field in update_data for field in ['usuario_id', 'fecha', 'hora']):
            usuario_id = update_data.get('usuario_id', agenda['usuario_id'])
            fecha = update_data.get('fecha', agenda['fecha'].isoformat())
            hora = update_data.get('hora', str(agenda['hora']))
            
            agenda_existente = Agenda.get_agenda_por_horario(usuario_id, fecha, hora)
            if agenda_existente and agenda_existente['id'] != agenda_id:
                return jsonify({'error': 'Ya existe una agenda para ese médico en ese horario'}), 400
        
        # Actualizar agenda
        Agenda.actualizar_agenda(agenda_id, update_data)
        
        return jsonify({
            'message': 'Agenda actualizada exitosamente',
            'agenda_id': agenda_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al actualizar agenda: {str(e)}'}), 500

@agendador_bp.route('/agendas/<int:agenda_id>', methods=['DELETE'])
@jwt_required()
def cancelar_agenda(agenda_id):
    """
    Cancelar agenda (marcar como cancelada en lugar de eliminar)
    """
    try:
        current_user = get_jwt_identity()
        
        if current_user['rol'] != 'scheduler':
            return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
        
        # Verificar que la agenda existe
        agenda = Agenda.get_by_id(agenda_id)
        if not agenda:
            return jsonify({'error': 'Agenda no encontrada'}), 404
        
        # No permitir cancelar agendas ya completadas
        if agenda['estado'] == 'completada':
            return jsonify({'error': 'No se puede cancelar una agenda ya completada'}), 400
        
        # Marcar como cancelada
        Agenda.actualizar_agenda(agenda_id, {'estado': 'cancelada'})
        
        return jsonify({
            'message': 'Agenda cancelada exitosamente',
            'agenda_id': agenda_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al cancelar agenda: {str(e)}'}), 500

@agendador_bp.route('/disponibilidad', methods=['GET'])
@jwt_required()
def get_disponibilidad():
    """
    Obtener horarios disponibles para un médico en un centro y fecha específicos
    """
    try:
        current_user = get_jwt_identity()
        
        if current_user['rol'] != 'scheduler':
            return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
        
        # Obtener parámetros
        usuario_id = request.args.get('usuario_id')
        centro_salud_id = request.args.get('centro_salud_id')
        fecha_str = request.args.get('fecha', datetime.now().date().isoformat())
        
        if not usuario_id or not centro_salud_id:
            return jsonify({'error': 'Los parámetros usuario_id y centro_salud_id son requeridos'}), 400
        
        # Verificar formato de fecha
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        # Obtener horarios ocupados para ese médico en esa fecha
        horarios_ocupados = Agenda.get_horarios_ocupados(usuario_id, centro_salud_id, fecha)
        
        # Generar horarios disponibles (8:00 - 18:00, cada 30 minutos)
        horarios_disponibles = generar_horarios_disponibles(horarios_ocupados, fecha)
        
        return jsonify({
            'fecha': fecha.isoformat(),
            'medico_id': usuario_id,
            'centro_salud_id': centro_salud_id,
            'horarios_disponibles': horarios_disponibles,
            'total_disponibles': len(horarios_disponibles)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener disponibilidad: {str(e)}'}), 500

@agendador_bp.route('/medicos', methods=['GET'])
@jwt_required()
def get_medicos():
    """
    Obtener lista de médicos para agendamiento
    """
    try:
        current_user = get_jwt_identity()
        
        if current_user['rol'] != 'scheduler':
            return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
        
        centro_salud_id = request.args.get('centro_salud_id')
        
        query = "SELECT id, rut, nombre, apellido, especialidad FROM usuarios WHERE rol = 'health-worker' AND activo = true"
        params = []
        
        if centro_salud_id:
            query += " AND id IN (SELECT usuario_id FROM usuarios_centros WHERE centro_salud_id = %s AND activo = true)"
            params.append(centro_salud_id)
        
        query += " ORDER BY nombre, apellido"
        
        medicos = Agenda.execute_custom_query(query, params, fetch=True)
        
        medicos_list = []
        for medico in medicos:
            medicos_list.append({
                'id': medico['id'],
                'rut': medico['rut'],
                'nombre': medico['nombre'],
                'apellido': medico['apellido'],
                'especialidad': medico['especialidad']
            })
        
        return jsonify({'medicos': medicos_list}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener médicos: {str(e)}'}), 500


def generar_horarios_disponibles(horarios_ocupados, fecha):
    """
    Generar lista de horarios disponibles excluyendo los ocupados
    """
    try:
        print(f"🔍 DEBUG - Iniciando generar_horarios_disponibles")
        print(f"🔍 DEBUG - Fecha: {fecha}")
        print(f"🔍 DEBUG - Horarios ocupados recibidos: {horarios_ocupados}")

        # Horario de trabajo: 8:00 - 18:00
        horario_inicio = time(8, 0)
        horario_fin = time(18, 0)
        
        # Generar todos los horarios posibles cada 30 minutos
        todos_horarios = []
        hora_actual = horario_inicio
        
        while hora_actual < horario_fin:
            todos_horarios.append(hora_actual)
            
            # Calcular siguiente hora de forma segura
            total_minutos = hora_actual.hour * 60 + hora_actual.minute + 30
            nueva_hora = total_minutos // 60
            nuevo_minuto = total_minutos % 60
            
            # Validar que no nos pasemos de 23:59
            if nueva_hora >= 24:
                break
                
            hora_actual = time(nueva_hora, nuevo_minuto)
            print(f"🔍 DEBUG - Siguiente hora: {hora_actual}")

        print(f"🔍 DEBUG - Todos los horarios generados: {[str(h) for h in todos_horarios]}")

        # Convertir horarios ocupados a time objects para comparación
        ocupados_set = set()
        if horarios_ocupados:
            for ocupado in horarios_ocupados:
                try:
                    hora_value = ocupado.get('hora')
                    print(f"🔍 DEBUG - Procesando hora ocupada: {hora_value}, tipo: {type(hora_value)}")
                    
                    if isinstance(hora_value, time):
                        # Ya es un objeto time, usar directamente
                        ocupados_set.add(hora_value)
                    elif isinstance(hora_value, str):
                        # Convertir string a time
                        hora_limpia = hora_value.strip()
                        
                        # Manejar diferentes formatos
                        if ':' in hora_limpia:
                            partes = hora_limpia.split(':')
                            horas = int(partes[0])
                            minutos = int(partes[1]) if len(partes) > 1 else 0
                            
                            # Validar rangos
                            if 0 <= horas < 24 and 0 <= minutos < 60:
                                hora_time = time(horas, minutos)
                                ocupados_set.add(hora_time)
                                print(f"✅ DEBUG - Hora convertida: {hora_time}")
                            else:
                                print(f"⚠️ Hora inválida (fuera de rango): {hora_limpia}")
                        else:
                            print(f"⚠️ Formato de hora no reconocido: {hora_limpia}")
                    else:
                        print(f"⚠️ Tipo de hora no manejado: {type(hora_value)}")
                        
                except Exception as e:
                    print(f"❌ Error procesando hora ocupada {ocupado}: {str(e)}")
                    continue

        print(f"🔍 DEBUG - Horarios ocupados finales: {[str(h) for h in ocupados_set]}")

        # Filtrar horarios disponibles
        disponibles = []
        for hora in todos_horarios:
            if hora not in ocupados_set:
                # Convertir a string en formato HH:MM
                hora_str = hora.strftime('%H:%M')
                disponibles.append(hora_str)

        print(f"✅ DEBUG - Horarios disponibles finales: {disponibles}")
        return disponibles
        
    except Exception as e:
        print(f"❌ ERROR en generar_horarios_disponibles: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        return []

@agendador_bp.route('/medicos-especialidad', methods=['GET'])
@jwt_required()
def get_medicos_por_especialidad():
    """
    Obtener médicos filtrados por especialidad
    """
    try:
        current_user = get_jwt_identity()
        
        if current_user['rol'] != 'scheduler':
            return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
        
        especialidad = request.args.get('especialidad')
        
        if not especialidad:
            return jsonify({'error': 'El parámetro especialidad es requerido'}), 400
        
        query = """
        SELECT id, rut, nombre, apellido, especialidad 
        FROM usuarios 
        WHERE rol = 'health-worker' 
        AND activo = true 
        AND especialidad = %s
        ORDER BY nombre, apellido
        """
        
        medicos = Agenda.execute_custom_query(query, (especialidad,), fetch=True)
        
        medicos_list = []
        for medico in medicos:
            medicos_list.append({
                'id': medico['id'],
                'rut': medico['rut'],
                'nombre': medico['nombre'],
                'apellido': medico['apellido'],
                'especialidad': medico['especialidad']
            })
        
        return jsonify({'medicos': medicos_list}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener médicos: {str(e)}'}), 500
    
@agendador_bp.route('/especialidades', methods=['GET'])
@jwt_required()
def get_especialidades():
    """
    Obtener lista de especialidades disponibles
    """
    try:
        current_user = get_jwt_identity()
        
        if current_user['rol'] != 'scheduler':
            return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
        
        query = "SELECT DISTINCT especialidad FROM usuarios WHERE rol = 'health-worker' AND activo = true AND especialidad IS NOT NULL ORDER BY especialidad"
        
        especialidades = Agenda.execute_custom_query(query, fetch=True)
        
        especialidades_list = [esp['especialidad'] for esp in especialidades]
        
        return jsonify({'especialidades': especialidades_list}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener especialidades: {str(e)}'}), 500
    

@staticmethod
def get_horarios_ocupados(usuario_id, centro_salud_id, fecha):
    """
    Obtener horarios ocupados para un médico en una fecha específica
    """
    try:
        print(f"🔍 DEBUG - get_horarios_ocupados: usuario_id={usuario_id}, centro_salud_id={centro_salud_id}, fecha={fecha}")
        
        query = """
        SELECT hora 
        FROM agendas 
        WHERE usuario_id = %s 
        AND centro_salud_id = %s 
        AND fecha = %s 
        AND estado NOT IN ('cancelada')
        ORDER BY hora
        """
        result = db.execute_query(query, (usuario_id, centro_salud_id, fecha), fetch=True)
        
        print(f"🔍 DEBUG - Horarios ocupados encontrados: {result}")
        return result
        
    except Exception as e:
        print(f"❌ ERROR en get_horarios_ocupados: {str(e)}")
        return []