from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.database import db

diagnosticos_bp = Blueprint('diagnosticos', __name__)

@diagnosticos_bp.route('/buscar', methods=['GET'])
@jwt_required()
def buscar_diagnosticos():
    try:
        termino = request.args.get('q', '').strip()
        limite = request.args.get('limit', 20, type=int)
        
        if not termino or len(termino) < 2:
            return jsonify({'diagnosticos': [], 'total': 0}), 200
        
        print(f"🔍 DEBUG - Buscando diagnósticos: '{termino}', límite: {limite}")
        
        # Usar la función de búsqueda mejorada de PostgreSQL con ranking
        query = """
        SELECT id, nombre, codigo_cie10, categoria, relevancia 
        FROM buscar_diagnosticos(%s)
        ORDER BY relevancia DESC
        LIMIT %s
        """
        
        resultados = db.execute_query(query, (termino, limite), fetch=True)
        
        print(f"✅ DEBUG - Encontrados {len(resultados) if resultados else 0} diagnósticos")
        
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
        print(f"❌ ERROR en buscar_diagnosticos: {str(e)}")
        return jsonify({'error': f'Error al buscar diagnósticos: {str(e)}'}), 500

@diagnosticos_bp.route('/sugerencias', methods=['GET'])
@jwt_required()
def obtener_sugerencias_rapidas():
    """
    Endpoint para obtener sugerencias rápidas (diagnósticos comunes)
    """
    try:
        limite = request.args.get('limit', 50, type=int)
        categoria = request.args.get('categoria')
        
        query = """
        SELECT id, nombre, codigo_cie10, categoria 
        FROM diagnosticos 
        WHERE 1=1
        """
        params = []
        
        if categoria:
            query += " AND categoria = %s"
            params.append(categoria)
        
        query += " ORDER BY nombre LIMIT %s"
        params.append(limite)
        
        resultados = db.execute_query(query, params, fetch=True)
        
        sugerencias = []
        if resultados:
            for diag in resultados:
                sugerencias.append({
                    'id': diag['id'],
                    'nombre': diag['nombre'],
                    'codigo_cie10': diag['codigo_cie10'],
                    'categoria': diag['categoria'],
                    'display_text': f"{diag['codigo_cie10']} - {diag['nombre']}" if diag['codigo_cie10'] else diag['nombre']
                })
        
        return jsonify({'sugerencias': sugerencias}), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_sugerencias_rapidas: {str(e)}")
        return jsonify({'error': f'Error al obtener sugerencias: {str(e)}'}), 500

@diagnosticos_bp.route('/categorias', methods=['GET'])
@jwt_required()
def obtener_categorias():
    """
    Obtener lista de categorías únicas para filtrado
    """
    try:
        query = "SELECT DISTINCT categoria FROM diagnosticos WHERE categoria IS NOT NULL ORDER BY categoria"
        
        resultados = db.execute_query(query, fetch=True)
        
        categorias = [cat['categoria'] for cat in resultados] if resultados else []
        
        return jsonify({'categorias': categorias}), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_categorias: {str(e)}")
        return jsonify({'error': f'Error al obtener categorías: {str(e)}'}), 500

@diagnosticos_bp.route('/por-codigo/<codigo>', methods=['GET'])
@jwt_required()
def obtener_diagnostico_por_codigo(codigo):
    """
    Obtener diagnóstico específico por código CIE-10
    """
    try:
        query = "SELECT id, nombre, codigo_cie10, categoria FROM diagnosticos WHERE codigo_cie10 = %s"
        
        diagnostico = db.execute_query(query, (codigo,), fetch_one=True)
        
        if not diagnostico:
            return jsonify({'error': 'Diagnóstico no encontrado'}), 404
        
        resultado = {
            'id': diagnostico['id'],
            'nombre': diagnostico['nombre'],
            'codigo_cie10': diagnostico['codigo_cie10'],
            'categoria': diagnostico['categoria'],
            'display_text': f"{diagnostico['codigo_cie10']} - {diagnostico['nombre']}" if diagnostico['codigo_cie10'] else diagnostico['nombre']
        }
        
        return jsonify({'diagnostico': resultado}), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_diagnostico_por_codigo: {str(e)}")
        return jsonify({'error': f'Error al obtener diagnóstico: {str(e)}'}), 500

@diagnosticos_bp.route('/<int:diagnostico_id>', methods=['GET'])
@jwt_required()
def obtener_diagnostico_por_id(diagnostico_id):
    """
    Obtener diagnóstico específico por ID
    """
    try:
        query = "SELECT id, nombre, codigo_cie10, categoria FROM diagnosticos WHERE id = %s"
        
        diagnostico = db.execute_query(query, (diagnostico_id,), fetch_one=True)
        
        if not diagnostico:
            return jsonify({'error': 'Diagnóstico no encontrado'}), 404
        
        resultado = {
            'id': diagnostico['id'],
            'nombre': diagnostico['nombre'],
            'codigo_cie10': diagnostico['codigo_cie10'],
            'categoria': diagnostico['categoria'],
            'display_text': f"{diagnostico['codigo_cie10']} - {diagnostico['nombre']}" if diagnostico['codigo_cie10'] else diagnostico['nombre']
        }
        
        return jsonify({'diagnostico': resultado}), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_diagnostico_por_id: {str(e)}")
        return jsonify({'error': f'Error al obtener diagnóstico: {str(e)}'}), 500