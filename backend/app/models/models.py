from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.database import db
from datetime import datetime
import bcrypt

class Usuario:
    @staticmethod
    def get_by_rut(rut):
        query = "SELECT * FROM usuarios WHERE rut = %s AND activo = true"
        return db.execute_query(query, (rut,), fetch_one=True)
    
    @staticmethod
    def verify_password(stored_hash, password):
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    
    @staticmethod
    def get_by_id(user_id):
        query = "SELECT id, rut, nombre, apellido, rol, especialidad FROM usuarios WHERE id = %s AND activo = true"
        return db.execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def create(user_data):
        """
        Crear nuevo usuario con contraseña hasheada
        """
        query = """
        INSERT INTO usuarios (rut, nombre, apellido, contraseña_hash, rol, especialidad, activo)
        VALUES (%s, %s, %s, %s, %s, %s, true)
        RETURNING id, rut, nombre, apellido, rol, especialidad, activo, created_at
        """
        params = [
            user_data['rut'],
            user_data['nombre'],
            user_data['apellido'],
            user_data['contraseña_hash'],
            user_data['rol'],
            user_data.get('especialidad')
        ]
        return db.execute_query(query, params, fetch_one=True)
    
    @staticmethod
    def execute_custom_query(query, params=None, fetch=False, fetch_one=False):
        """
        Ejecutar consulta personalizada
        """
        return db.execute_query(query, params, fetch, fetch_one)

class CentroSalud:
    @staticmethod
    def get_all():
        query = "SELECT * FROM centros_salud WHERE activo = true ORDER BY nombre"
        return db.execute_query(query, fetch=True)
    
    @staticmethod
    def get_by_id(centro_id):
        query = "SELECT * FROM centros_salud WHERE id = %s AND activo = true"
        return db.execute_query(query, (centro_id,), fetch_one=True)
class Paciente:
    @staticmethod
    def get_by_id(paciente_id):
        query = "SELECT * FROM pacientes WHERE id = %s"
        return db.execute_query(query, (paciente_id,), fetch_one=True)
    
    @staticmethod
    def get_by_rut(rut):
        query = "SELECT * FROM pacientes WHERE rut = %s"
        return db.execute_query(query, (rut,), fetch_one=True)
    
    @staticmethod
    def search_by_lastname(apellido):
        query = "SELECT * FROM pacientes WHERE LOWER(apellido) LIKE LOWER(%s) ORDER BY apellido, nombre"
        return db.execute_query(query, (f'{apellido}%',), fetch=True)
    
    @staticmethod
    def create(paciente_data):
        """
        Crear nuevo paciente con todos los campos
        """
        query = """
        INSERT INTO pacientes (rut, nombre, apellido, telefono, edad, genero, direccion, fecha_nacimiento, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, rut, nombre, apellido, telefono, edad, genero, direccion, fecha_nacimiento, email
        """
        params = [
            paciente_data['rut'],
            paciente_data['nombre'],
            paciente_data['apellido'],
            paciente_data.get('telefono'),
            paciente_data.get('edad'),
            paciente_data.get('genero'),
            paciente_data.get('direccion'),
            paciente_data.get('fecha_nacimiento'),
            paciente_data.get('email')
        ]
        
        print(f"🔍 DEBUG - Ejecutando creación de paciente: {query}")
        print(f"🔍 DEBUG - Parámetros: {params}")
        
        result = db.execute_query(query, params, fetch_one=True)
        print(f"🔍 DEBUG - Resultado de creación: {result}")
        
        return result
    
    
class Agenda:
    @staticmethod
    def get_daily_agenda(usuario_id, centro_salud_id, fecha):
        query = """
        SELECT 
            a.id as agenda_id,
            a.fecha,
            a.hora,
            a.estado as estado_agenda,
            a.tipo_consulta,
            a.n_ficha,
            a.n_carpeta,
            p.rut as paciente_rut,
            p.nombre as paciente_nombre,
            p.apellido as paciente_apellido,
            p.telefono as paciente_telefono,
            p.edad as paciente_edad,
            p.genero as paciente_genero,
            c.estado_hora,
            c.estado_atencion,
            c.modalidad_atencion,  -- ¡IMPORTANTE: incluir este campo!
            c.diagnostico
        FROM agendas a
        JOIN pacientes p ON a.paciente_id = p.id
        LEFT JOIN consultas c ON c.agenda_id = a.id
        WHERE a.usuario_id = %s
        AND a.centro_salud_id = %s
        AND a.fecha = %s
        ORDER BY a.hora
        """
        return db.execute_query(query, (usuario_id, centro_salud_id, fecha), fetch=True)
    
    @staticmethod
    def get_by_id(agenda_id):
        query = "SELECT * FROM agendas WHERE id = %s"
        return db.execute_query(query, (agenda_id,), fetch_one=True)
    
    @staticmethod
    def update_status(agenda_id, estado, consulta_id=None):
        """
        Actualiza el estado de una agenda
        """
        print(f"🔍 DEBUG - Ejecutando update_status: agenda_id={agenda_id}, estado={estado}, consulta_id={consulta_id}")
        
        query = """
        UPDATE agendas 
        SET estado = %s, 
            consulta_id = COALESCE(%s, consulta_id),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        try:
            db.execute_query(query, (estado, consulta_id, agenda_id))
            print(f"✅ DEBUG - Agenda {agenda_id} actualizada a estado: {estado}")
            return True
        except Exception as e:
            print(f"❌ ERROR en update_status: {str(e)}")
            return False
    
    @staticmethod
    def get_by_id(agenda_id):
        query = "SELECT * FROM agendas WHERE id = %s"
        return db.execute_query(query, (agenda_id,), fetch_one=True)
    
    @staticmethod
    def get_detalle_completo(agenda_id, usuario_id=None):
        """
        Obtiene el detalle completo de una agenda incluyendo paciente y consulta
        """
        print(f"🔍 DEBUG get_detalle_completo - agenda_id: {agenda_id}, usuario_id: {usuario_id}")
        
        query = """
        SELECT 
            a.id as agenda_id,
            a.fecha,
            a.hora,
            a.estado as estado_agenda,
            a.tipo_consulta,
            a.n_ficha,
            a.n_carpeta,
            a.usuario_id,
            a.centro_salud_id,
            p.id as paciente_id,
            p.rut as paciente_rut,
            p.nombre as paciente_nombre,
            p.apellido as paciente_apellido,
            p.telefono as paciente_telefono,
            p.edad as paciente_edad,
            p.genero as paciente_genero,
            p.direccion as paciente_direccion,
            p.fecha_nacimiento as paciente_fecha_nacimiento,
            p.email as paciente_email,
            c.id as consulta_id,
            c.estado_hora,
            c.estado_atencion,
            c.modalidad_atencion,
            c.actividad,
            c.tipo_alta,
            c.diagnostico,
            c.observaciones,
            c.ges,
            c.ingreso_diag,
            c.control_tto,
            c.egreso,
            c.pscv,
            c.morbilidad,
            c.psm,
            c.cns,
            c.lmp_lme,
            c.consejeria_lm,
            c.embarazada,
            c.visita_domic,
            c.dep_severa,
            c.remoto,
            c.created_at as consulta_created_at,
            c.updated_at as consulta_updated_at,
            u.nombre as medico_nombre,
            u.apellido as medico_apellido,
            u.especialidad as medico_especialidad,
            cs.nombre as centro_nombre
        FROM agendas a
        JOIN pacientes p ON a.paciente_id = p.id
        LEFT JOIN consultas c ON c.agenda_id = a.id
        JOIN usuarios u ON a.usuario_id = u.id
        JOIN centros_salud cs ON a.centro_salud_id = cs.id
        WHERE a.id = %s
        """
        
        params = [agenda_id]
        
        # Si se proporciona usuario_id, verificar que la agenda pertenezca al usuario
        if usuario_id:
            query += " AND a.usuario_id = %s"
            params.append(usuario_id)
        
        print(f"🔍 DEBUG - Query: {query}")
        print(f"🔍 DEBUG - Parámetros: {params}")
        
        result = db.execute_query(query, params, fetch_one=True)
        print(f"🔍 DEBUG - Resultado de la query: {result}")
        
        return result



    @staticmethod
    def get_agenda_por_horario(usuario_id, fecha, hora):
        """
        Verificar si ya existe una agenda para un médico en un horario específico
        """
        query = "SELECT * FROM agendas WHERE usuario_id = %s AND fecha = %s AND hora = %s"
        return db.execute_query(query, (usuario_id, fecha, hora), fetch_one=True)
    
    @staticmethod
    def crear_agenda(paciente_id, usuario_id, centro_salud_id, fecha, hora, tipo_consulta='consulta', n_ficha=None, n_carpeta=None):
        """
        Crear nueva agenda médica
        """
        query = """
        INSERT INTO agendas (paciente_id, usuario_id, centro_salud_id, fecha, hora, tipo_consulta, n_ficha, n_carpeta, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'agendada')
        RETURNING *
        """
        params = [paciente_id, usuario_id, centro_salud_id, fecha, hora, tipo_consulta, n_ficha, n_carpeta]
        return db.execute_query(query, params, fetch_one=True)
    
    @staticmethod
    def actualizar_agenda(agenda_id, update_data):
        """
        Actualizar agenda existente
        """
        if not update_data:
            return
        
        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
        query = f"UPDATE agendas SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        
        params = list(update_data.values())
        params.append(agenda_id)
        
        db.execute_query(query, params)
    
    @staticmethod
    def get_horarios_ocupados(usuario_id, centro_salud_id, fecha):
        """
        Obtener horarios ocupados para un médico en una fecha específica
        """
        query = """
        SELECT hora 
        FROM agendas 
        WHERE usuario_id = %s 
        AND centro_salud_id = %s 
        AND fecha = %s 
        AND estado NOT IN ('cancelada')
        ORDER BY hora
        """
        return db.execute_query(query, (usuario_id, centro_salud_id, fecha), fetch=True)
    
    @staticmethod
    def execute_custom_query(query, params=None, fetch=False, fetch_one=False):
        """
        Ejecutar consulta personalizada (para queries complejas)
        """
        return db.execute_query(query, params, fetch, fetch_one)
    
class Consulta:
    @staticmethod
    def get_by_agenda_id(agenda_id):
        query = """
        SELECT c.*, d.nombre as diagnostico_nombre, d.codigo_cie10 
        FROM consultas c 
        LEFT JOIN diagnosticos d ON c.diagnostico_id = d.id 
        WHERE c.agenda_id = %s
        """
        return db.execute_query(query, (agenda_id,), fetch_one=True)
    
    @staticmethod
    def create(consulta_data):
        """
        Crear nueva consulta - 28 parámetros (agregando diagnostico_id)
        """
        query = """
        INSERT INTO consultas (
            agenda_id, paciente_id, usuario_id, centro_salud_id,
            fecha_consulta, hora_consulta, estado_hora, estado_atencion,
            modalidad_atencion, actividad, tipo_alta, diagnostico,
            observaciones, ges, ingreso_diag, control_tto, egreso,
            pscv, morbilidad, psm, cns, lmp_lme, consejeria_lm,
            embarazada, visita_domic, dep_severa, remoto, diagnostico_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        print(f"🔍 DEBUG - Ejecutando CREATE con {len(consulta_data)} parámetros")
        return db.execute_query(query, consulta_data, fetch_one=True)
    
    @staticmethod
    def update(consulta_id, update_data):
        """
        Actualizar consulta existente - 22 campos + 1 ID = 23 parámetros (agregando diagnostico_id)
        """
        query = """
        UPDATE consultas SET
            estado_hora = %s,
            estado_atencion = %s,
            modalidad_atencion = %s,
            actividad = %s,
            tipo_alta = %s,
            diagnostico = %s,
            observaciones = %s,
            ges = %s,
            ingreso_diag = %s,
            control_tto = %s,
            egreso = %s,
            pscv = %s,
            morbilidad = %s,
            psm = %s,
            cns = %s,
            lmp_lme = %s,
            consejeria_lm = %s,
            embarazada = %s,
            visita_domic = %s,
            dep_severa = %s,
            remoto = %s,
            diagnostico_id = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        # Agregar el consulta_id al final
        params = update_data + [consulta_id]
        print(f"🔍 DEBUG - Ejecutando UPDATE con {len(params)} parámetros")
        db.execute_query(query, params)
        return consulta_id

class SesionTrabajo:
    @staticmethod
    def create_sesion(usuario_id, centro_salud_id, fecha):
        """
        Crea o retorna una sesión existente usando UPSERT
        Sin la columna updated_at
        """
        query = """
        INSERT INTO sesiones_trabajo (usuario_id, centro_salud_id, fecha, activa, hora_inicio)
        VALUES (%s, %s, %s, true, CURRENT_TIME)
        ON CONFLICT (usuario_id, centro_salud_id, fecha) 
        DO UPDATE SET 
            activa = true,
            hora_inicio = CASE 
                WHEN sesiones_trabajo.hora_inicio IS NULL THEN CURRENT_TIME 
                ELSE sesiones_trabajo.hora_inicio 
            END
        RETURNING id, usuario_id, centro_salud_id, fecha, hora_inicio, activa
        """
        return db.execute_query(query, (usuario_id, centro_salud_id, fecha), fetch_one=True)
    
    @staticmethod
    def get_sesion_activa(usuario_id, centro_salud_id, fecha):
        """
        Obtiene una sesión activa existente
        """
        query = """
        SELECT * FROM sesiones_trabajo 
        WHERE usuario_id = %s 
        AND centro_salud_id = %s 
        AND fecha = %s 
        AND activa = true
        """
        return db.execute_query(query, (usuario_id, centro_salud_id, fecha), fetch_one=True)
    
    @staticmethod
    def cerrar_sesion(sesion_id):
        """
        Cierra una sesión de trabajo estableciendo activa = false y hora_fin
        """
        query = """
        UPDATE sesiones_trabajo 
        SET activa = false, 
            hora_fin = CURRENT_TIME,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        db.execute_query(query, (sesion_id,))
    
    @staticmethod
    def get_sesiones_por_usuario(usuario_id, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene todas las sesiones de un usuario en un rango de fechas
        """
        query = """
        SELECT st.*, cs.nombre as centro_nombre
        FROM sesiones_trabajo st
        JOIN centros_salud cs ON st.centro_salud_id = cs.id
        WHERE st.usuario_id = %s
        """
        params = [usuario_id]
        
        if fecha_inicio and fecha_fin:
            query += " AND st.fecha BETWEEN %s AND %s"
            params.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            query += " AND st.fecha >= %s"
            params.append(fecha_inicio)
        elif fecha_fin:
            query += " AND st.fecha <= %s"
            params.append(fecha_fin)
        
        query += " ORDER BY st.fecha DESC, st.hora_inicio DESC"
        
        return db.execute_query(query, params, fetch=True)
    @staticmethod
    def create_or_get_sesion(usuario_id, centro_salud_id, fecha):
        """
        Método robusto que maneja múltiples escenarios para crear/obtener sesión
        """
        try:
            # Primero intentar obtener sesión existente
            sesion_existente = SesionTrabajo.get_sesion_activa(usuario_id, centro_salud_id, fecha)
            if sesion_existente:
                return sesion_existente
            
            # Si no existe, crear nueva con UPSERT
            return SesionTrabajo.create_sesion(usuario_id, centro_salud_id, fecha)
            
        except Exception as e:
            # Si hay algún error, intentar recuperar la sesión existente
            print(f"⚠️ Error creando sesión: {e}")
            sesion_existente = SesionTrabajo.get_sesion_activa(usuario_id, centro_salud_id, fecha)
            if sesion_existente:
                return sesion_existente
            else:
                # Último recurso: crear sin RETURNING
                query = """
                INSERT INTO sesiones_trabajo (usuario_id, centro_salud_id, fecha, activa)
                VALUES (%s, %s, %s, true)
                ON CONFLICT (usuario_id, centro_salud_id, fecha) 
                DO NOTHING
                """
                db.execute_query(query, (usuario_id, centro_salud_id, fecha))
                
                # Obtener la sesión recién creada
                return SesionTrabajo.get_sesion_activa(usuario_id, centro_salud_id, fecha)
            