import re

def validar_cedula(cedula: str) -> bool:
    if not cedula.isdigit() or len(cedula) != 10:
        return False
    return True

    


def validar_ruc(ruc):
    if not ruc.isdigit():
        return False

    if len(ruc) != 13:
        return False

    if not ruc.endswith("001"):
        return False

    return True
