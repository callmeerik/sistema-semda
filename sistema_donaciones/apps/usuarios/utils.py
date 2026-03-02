import re

def validar_password(password: str):
    """Valida fortaleza básica de contraseña"""

    if len(password) < 7:
        return False, "La contraseña debe tener al menos 7 caracteres."

    if " " in password:
        return False, "La contraseña no debe contener espacios."

    if not re.search(r"[A-Z]", password):
        return False, "Debe incluir al menos una letra mayúscula."

    if not re.search(r"[a-z]", password):
        return False, "Debe incluir al menos una letra minúscula."

    if not re.search(r"\d", password):
        return False, "Debe incluir al menos un número."

    # opcional pero recomendable
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Debe incluir al menos un símbolo."

    return True, ""