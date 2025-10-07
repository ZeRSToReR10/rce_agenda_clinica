import sys
import os

# Añadir el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.models import Usuario
from app.utils.security import hash_password

def create_initial_admin():
    """Crear usuario admin inicial si no existe"""
    app = create_app()
    
    with app.app_context():
        # Verificar si ya existe un admin
        existing_admin = Usuario.get_by_rut('20.709.366-1')
        if existing_admin:
            print("✅ El usuario admin ya existe")
            return
        
        # Datos del admin
        admin_data = {
            'rut': '20.709.366-1',
            'nombre': 'Administrador',
            'apellido': 'Sistema',
            'contraseña_hash': hash_password('LaMc2019'),  # Contraseña por defecto
            'rol': 'admin',
            'especialidad': 'Administración'
        }
        
        try:
            # Crear el admin
            nuevo_admin = Usuario.create(admin_data)
            print("✅ Usuario admin creado exitosamente:")
            print(f"   RUT: {nuevo_admin['rut']}")
            print(f"   Nombre: {nuevo_admin['nombre']} {nuevo_admin['apellido']}")
            print(f"   Rol: {nuevo_admin['rol']}")
            print(f"   Contraseña: LaMc2019")
            
        except Exception as e:
            print(f"❌ Error al crear usuario admin: {str(e)}")

if __name__ == '__main__':
    create_initial_admin()