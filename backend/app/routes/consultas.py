from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Consulta, Agenda, Paciente
from app.utils.validators import validate_required_fields
from datetime import datetime
from app.models.database import db

consultas_bp = Blueprint('consultas', __name__)

def map_consulta_status_to_agenda_status(estado_hora):
    """
    Mapea el estado de la consulta al estado correspondiente de la agenda
    """
    estado_mapping = {
        'Asignada': 'agendada',
        'ejecutada': 'completada',
        'no ejecutada': 'cancelada',
        'Ejecutada': 'completada',  # Por si acaso viene con mayúscula
        'No Ejecutada': 'cancelada'  # Por si acaso viene con mayúscula
    }
    return estado_mapping.get(estado_hora, 'agendada')

def obtener_id_diagnostico_por_texto(texto_diagnostico):
    """
    Extraer ID de diagnóstico del texto formateado o buscar por nombre
    """
    try:
        if not texto_diagnostico or texto_diagnostico.strip() == '':
            return None
            
        texto_diagnostico = texto_diagnostico.strip()
        print(f"🔍 DEBUG - Buscando ID para diagnóstico: '{texto_diagnostico}'")
        
        # Si el texto viene en formato "Código - Nombre", extraer el código
        if ' - ' in texto_diagnostico:
            partes = texto_diagnostico.split(' - ', 1)
            codigo = partes[0].strip()
            nombre = partes[1].strip()
            
            print(f"🔍 DEBUG - Formato detectado - Código: '{codigo}', Nombre: '{nombre}'")
            
            # Primero intentar buscar por código exacto
            query = "SELECT id FROM diagnosticos WHERE codigo_cie10 = %s"
            resultado = db.execute_query(query, (codigo,), fetch_one=True)
            
            if resultado:
                print(f"✅ DEBUG - Diagnóstico encontrado por código: {resultado['id']}")
                return resultado['id']
            
            # Si no encuentra por código, buscar por nombre
            query = "SELECT id FROM diagnosticos WHERE nombre ILIKE %s LIMIT 1"
            resultado = db.execute_query(query, (f"%{nombre}%",), fetch_one=True)
            
            if resultado:
                print(f"✅ DEBUG - Diagnóstico encontrado por nombre: {resultado['id']}")
                return resultado['id']
        
        # Si no está en formato código-nombre, buscar directamente por nombre
        query = "SELECT id FROM diagnosticos WHERE nombre ILIKE %s LIMIT 1"
        resultado = db.execute_query(query, (f"%{texto_diagnostico}%",), fetch_one=True)
        
        if resultado:
            print(f"✅ DEBUG - Diagnóstico encontrado por texto completo: {resultado['id']}")
            return resultado['id']
        
        print(f"⚠️ DEBUG - No se encontró diagnóstico para: '{texto_diagnostico}'")
        return None
        
    except Exception as e:
        print(f"❌ ERROR al obtener ID de diagnóstico: {e}")
        return None

@consultas_bp.route('/detalle/<int:agenda_id>', methods=['GET'])
@jwt_required()
def get_detalle_consulta(agenda_id):
    try:
        current_user = get_jwt_identity()
        
        # Obtener datos de la agenda y paciente
        agenda = Agenda.get_by_id(agenda_id)
        if not agenda:
            return jsonify({'error': 'Agenda no encontrada'}), 404
        
        paciente = Paciente.get_by_id(agenda['paciente_id'])
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        # Obtener consulta existente (si existe) con información del diagnóstico
        consulta = Consulta.get_by_agenda_id(agenda_id)
        
        # Formatear respuesta
        response_data = {
            'agenda': {
                'id': agenda['id'],
                'fecha': agenda['fecha'].isoformat(),
                'hora': str(agenda['hora']),
                'tipo_consulta': agenda['tipo_consulta'],
                'n_ficha': agenda['n_ficha'],
                'n_carpeta': agenda['n_carpeta'],
                'estado': agenda['estado']
            },
            'paciente': {
                'id': paciente['id'],
                'rut': paciente['rut'],
                'nombre': paciente['nombre'],
                'apellido': paciente['apellido'],
                'telefono': paciente['telefono'],
                'edad': paciente['edad'],
                'genero': paciente['genero'],
                'direccion': paciente['direccion']
            }
        }
        
        # Agregar datos de consulta si existe
        if consulta:
            consulta_data = {
                'id': consulta['id'],
                'estado_hora': consulta['estado_hora'],
                'estado_atencion': consulta['estado_atencion'],
                'modalidad_atencion': consulta['modalidad_atencion'],
                'actividad': consulta['actividad'],
                'tipo_alta': consulta['tipo_alta'],
                'diagnostico': consulta['diagnostico'],
                'observaciones': consulta['observaciones'],
                'ges': consulta['ges'],
                'ingreso_diag': consulta['ingreso_diag'],
                'control_tto': consulta['control_tto'],
                'egreso': consulta['egreso'],
                'pscv': consulta['pscv'],
                'morbilidad': consulta['morbilidad'],
                'psm': consulta['psm'],
                'cns': consulta['cns'],
                'lmp_lme': consulta['lmp_lme'],
                'consejeria_lm': consulta['consejeria_lm'],
                'embarazada': consulta['embarazada'],
                'visita_domic': consulta['visita_domic'],
                'dep_severa': consulta['dep_severa'],
                'remoto': consulta['remoto']
            }
            
            # Agregar información del diagnóstico si existe relación
            if consulta.get('diagnostico_nombre'):
                consulta_data['diagnostico_detalle'] = {
                    'id': consulta.get('diagnostico_id'),
                    'nombre': consulta['diagnostico_nombre'],
                    'codigo_cie10': consulta.get('codigo_cie10'),
                    'display_text': f"{consulta.get('codigo_cie10')} - {consulta['diagnostico_nombre']}" if consulta.get('codigo_cie10') else consulta['diagnostico_nombre']
                }
            
            response_data['consulta'] = consulta_data
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ ERROR en get_detalle_consulta: {str(e)}")
        return jsonify({'error': f'Error al obtener detalle de consulta: {str(e)}'}), 500

@consultas_bp.route('/guardar', methods=['POST'])
@jwt_required()
def guardar_consulta():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        print(f"🔍 DEBUG - Datos recibidos en guardar_consulta: {data}")
        
        # Validar campos requeridos
        required_fields = ['agenda_id', 'paciente_id', 'centro_salud_id']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return jsonify({'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        # Verificar si la agenda existe
        agenda = Agenda.get_by_id(data['agenda_id'])
        if not agenda:
            return jsonify({'error': 'Agenda no encontrada'}), 404
        
        # Obtener ID del diagnóstico si se proporciona texto de diagnóstico
        diagnostico_id = None
        texto_diagnostico = data.get('diagnostico', '')
        if texto_diagnostico and texto_diagnostico.strip():
            diagnostico_id = obtener_id_diagnostico_por_texto(texto_diagnostico)
            print(f"🔍 DEBUG - ID de diagnóstico encontrado: {diagnostico_id}")
        
        # Verificar si ya existe una consulta para esta agenda
        consulta_existente = Consulta.get_by_agenda_id(data['agenda_id'])
        
        print(f"🔍 DEBUG - Consulta existente: {consulta_existente}")
        
        if consulta_existente:
            # ACTUALIZAR CONSULTA EXISTENTE
            print(f"🔍 DEBUG - Actualizando consulta existente ID: {consulta_existente['id']}")
            
            update_data = [
                data.get('estado_hora', 'Asignada'),
                data.get('estado_atencion', 'en espera'),
                data.get('modalidad_atencion', 'presencial'),
                data.get('actividad', 'consulta'),
                data.get('tipo_alta', 'alta'),
                texto_diagnostico,  # Usar el texto original del diagnóstico
                data.get('observaciones', ''),
                data.get('ges', False),
                data.get('ingreso_diag', False),
                data.get('control_tto', False),
                data.get('egreso', False),
                data.get('pscv', False),
                data.get('morbilidad', False),
                data.get('psm', False),
                data.get('cns', False),
                data.get('lmp_lme', False),
                data.get('consejeria_lm', False),
                data.get('embarazada', False),
                data.get('visita_domic', False),
                data.get('dep_severa', False),
                data.get('remoto', False),
                diagnostico_id  # Nuevo parámetro para diagnóstico_id
            ]
            
            consulta_id = Consulta.update(consulta_existente['id'], update_data)
            message = 'Consulta actualizada exitosamente'
            
        else:
            # CREAR NUEVA CONSULTA
            print("🔍 DEBUG - Creando nueva consulta")
            
            create_data = [
                data['agenda_id'],
                data['paciente_id'],
                current_user['id'],
                data['centro_salud_id'],
                data.get('fecha_consulta', datetime.now().date().isoformat()),
                data.get('hora_consulta', datetime.now().time().strftime('%H:%M:%S')),
                data.get('estado_hora', 'Asignada'),
                data.get('estado_atencion', 'en espera'),
                data.get('modalidad_atencion', 'presencial'),
                data.get('actividad', 'consulta'),
                data.get('tipo_alta', 'alta'),
                texto_diagnostico,  # Usar el texto original del diagnóstico
                data.get('observaciones', ''),
                data.get('ges', False),
                data.get('ingreso_diag', False),
                data.get('control_tto', False),
                data.get('egreso', False),
                data.get('pscv', False),
                data.get('morbilidad', False),
                data.get('psm', False),
                data.get('cns', False),
                data.get('lmp_lme', False),
                data.get('consejeria_lm', False),
                data.get('embarazada', False),
                data.get('visita_domic', False),
                data.get('dep_severa', False),
                data.get('remoto', False),
                diagnostico_id  # Nuevo parámetro para diagnóstico_id
            ]
            
            result = Consulta.create(create_data)
            if not result:
                return jsonify({'error': 'No se pudo crear la consulta'}), 500
                
            consulta_id = result['id']
            message = 'Consulta creada exitosamente'

        # Actualizar estado de la agenda
        estado_hora = data.get('estado_hora', 'Asignada')
        estado_agenda = map_consulta_status_to_agenda_status(estado_hora)
        
        print(f"🔍 DEBUG - Actualizando agenda {data['agenda_id']} a estado: {estado_agenda}")
        
        # Usar la versión que maneja la posible falta de columna consulta_id
        Agenda.update_status(
            agenda_id=data['agenda_id'],
            estado=estado_agenda,
            consulta_id=consulta_id
        )
        
        return jsonify({
            'message': message,
            'consulta_id': consulta_id,
            'agenda_actualizada': True,
            'nuevo_estado_agenda': estado_agenda,
            'diagnostico_id_asignado': diagnostico_id
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en guardar_consulta: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        return jsonify({'error': f'Error al guardar consulta: {str(e)}'}), 500

@consultas_bp.route('/diagnostico/sugerir', methods=['GET'])
@jwt_required()
def sugerir_diagnosticos():
    """
    Endpoint para obtener sugerencias de diagnósticos basado en un término de búsqueda
    """
    try:
        termino = request.args.get('q', '').strip()
        limite = request.args.get('limit', 10, type=int)
        
        if not termino or len(termino) < 2:
            return jsonify({'diagnosticos': [], 'total': 0}), 200
        
        print(f"🔍 DEBUG - Buscando diagnósticos para: '{termino}'")
        
        # Usar la función de búsqueda de PostgreSQL
        query = """
        SELECT id, nombre, codigo_cie10, categoria, relevancia 
        FROM buscar_diagnosticos(%s)
        ORDER BY relevancia DESC
        LIMIT %s
        """
        
        resultados = db.execute_query(query, (termino, limite), fetch=True)
        
        diagnosticos_list = []
        if resultados:
            for diag in resultados:
                diagnosticos_list.append({
                    'id': diag['id'],
                    'nombre': diag['nombre'],
                    'codigo_cie10': diag['codigo_cie10'],
                    'categoria': diag['categoria'],
                    'relevancia': float(diag['relevancia']) if diag['relevancia'] else 0.0,
                    'display_text': f"{diag['codigo_cie10']} - {diag['nombre']}" if diag['codigo_cie10'] else diag['nombre']
                })
        
        return jsonify({
            'diagnosticos': diagnosticos_list,
            'total': len(diagnosticos_list),
            'termino_busqueda': termino
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en sugerir_diagnosticos: {str(e)}")
        return jsonify({'error': f'Error al buscar diagnósticos: {str(e)}'}), 500