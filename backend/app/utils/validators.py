import re

def validate_rut(rut):
    """Valida formato de RUT chileno"""
    rut_pattern = re.compile(r'^(\d{1,3}(?:\.\d{3}){2}-[\dkK])$')
    rut_simple_pattern = re.compile(r'^(\d{7,8}-[\dkK])$')
    
    return bool(rut_pattern.match(rut)) or bool(rut_simple_pattern.match(rut))

def validate_email(email):
    """Valida formato de email"""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))

def validate_required_fields(data, required_fields):
    """Valida que los campos requeridos estén presentes"""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    return missing_fields