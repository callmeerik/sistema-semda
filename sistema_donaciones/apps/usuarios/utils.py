import re

def validar_password(password):
    """Validación de la contraseña"""
    
    # mínimo 7 caracteres
    if len(password) < 7:
        return False, "La contraseña debe tener al menos 7 caracteres."
    
    # al menos una mayúscula
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe incluir al menos una letra mayúscula."
    
    # al menos una minúscula
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe incluir al menos una letra minúscula."
    
    # al menos un número
    if not re.search(r"\d", password):
        return False, "La contraseña debe incluir al menos un número."
    
    return True, ""
