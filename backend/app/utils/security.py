import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_jwt_token(user_data):
    identity = {
        'id': user_data['id'],
        'rut': user_data['rut'],
        'nombre': user_data['nombre'],
        'apellido': user_data['apellido'],
        'rol': user_data['rol']
    }
    return create_access_token(identity=identity)