from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400
    
    # Configuración de la base de datos
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_PORT'] = os.getenv('DB_PORT', '5432')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'rce_database_new')
    app.config['DB_USER'] = os.getenv('DB_USER', 'rce_admin')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'LaMc2019')
    
    # Inicializar extensiones
    CORS(app)
    jwt = JWTManager(app)
    
    # Registrar blueprints - VERIFICA QUE ESTÉN ESTAS LÍNEAS
    from app.routes.auth import auth_bp
    from app.routes.agendas import agendas_bp
    from app.routes.consultas import consultas_bp
    from app.routes.pacientes import pacientes_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(agendas_bp, url_prefix='/api/agendas')
    app.register_blueprint(consultas_bp, url_prefix='/api/consultas')
    app.register_blueprint(pacientes_bp, url_prefix='/api/pacientes')
    
    return app