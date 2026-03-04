import re

def validar_cedula(cedula: str) -> bool:
    if not cedula.isdigit() or len(cedula) != 10:
        print("error digito no es")
        return False
    
    # obtner caracteres de provincia y tercer digito
    provincia = int(cedula[:2]) # dos primeros digitos
    tercer_digito = int( cedula[2] )

    # validacion de digitos de provincia (30 para el exterior)
    if not ( 1 <= provincia <= 24 or provincia == 30 ):
        print("error provincia")
        return False
    
    # validacion de cedula verdadera
    if tercer_digito >= 6:
        print("error tercer digito")
        return False
    
    coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]    
    suma = 0

    for i in range(9):
        valor = int( cedula[i] ) * coef[i]
        if valor > 9:
            valor -= 9
        suma += valor
    digito_verificador = ( 10 - (suma % 10) )
    return digito_verificador == int( cedula[9] )



def validar_ruc(ruc: str) -> bool:
    if not ruc.isdigit() or len(ruc) != 13:
        return False

    provincia = int(ruc[:2])
    tercer_digito = int(ruc[2])

    # 1. Validación de provincia (01-24 o 30)
    if not (1 <= provincia <= 24 or provincia == 30):
        return False

    # --- CASO: PERSONA NATURAL (0, 1, 2, 3, 4, 5) ---
    if tercer_digito < 6:
        if ruc[10:] != "001":  # Validación estricta según tu consulta
            return False
        return validar_cedula(ruc[:10])

    # --- CASO: EMPRESA PRIVADA / EXTRANJEROS (9) ---
    elif tercer_digito == 9:
        if ruc[10:] != "001":
            return False
        
        coef = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc[i]) * coef[i] for i in range(9))
        residuo = suma % 11
        
        # En Módulo 11, si residuo es 0, verificador es 0
        verificador_calc = 0 if residuo == 0 else 11 - residuo
        
        if verificador_calc == 10: return False # Caso inválido
        return verificador_calc == int(ruc[9])

    # --- CASO: EMPRESA PÚBLICA (6) ---
    elif tercer_digito == 6:
        # Las públicas suelen terminar en 0001
        if ruc[9:] != "0001":
            return False
            
        coef = [3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc[i]) * coef[i] for i in range(8))
        residuo = suma % 11
        
        verificador_calc = 0 if residuo == 0 else 11 - residuo
        
        if verificador_calc == 10: return False # Caso inválido
        return verificador_calc == int(ruc[8])

    return False