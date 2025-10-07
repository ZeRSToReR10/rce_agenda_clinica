import psycopg2
import psycopg2.extras
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        try:
            if self.connection is None or self.connection.closed:
                self.connection = psycopg2.connect(
                    host=current_app.config['DB_HOST'],
                    port=current_app.config['DB_PORT'],
                    database=current_app.config['DB_NAME'],
                    user=current_app.config['DB_USER'],
                    password=current_app.config['DB_PASSWORD']
                )
            return self.connection
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute(query, params)
            
            # Determinar si es SELECT o modificación
            is_select = query.strip().lower().startswith("select")
            
            if fetch_one:
                result = cursor.fetchone()
                if result is None:
                    return None
                if not isinstance(result, dict):
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, result))
            elif fetch:
                result = cursor.fetchall()
                if result and len(result) > 0:
                    columns = [desc[0] for desc in cursor.description]
                    result = [dict(zip(columns, row)) for row in result]
            else:
                result = None
            
            # Commit si no es SELECT
            if not is_select:
                conn.commit()
            
            return result
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def close_connection(self):
        if self.connection and not self.connection.closed:
            self.connection.close()

# Instancia global de la base de datos
db = Database()