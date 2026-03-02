import re

def validar_cedula(cedula: str) -> bool:
    if not cedula.isdigit() or len(cedula) != 10:
        return False
    
    # obtner caracteres de provincia y tercer digito
    provincia = int(cedula[:2]) # dos primeros digitos
    tercer_digito = int( cedula[2] )

    # validacion de digitos de provincia (30 para el exterior)
    if not ( 1 <= provincia <= 24 or provincia == 30 ):
        return False
    
    # validacion de cedula verdadera
    if tercer_digito >= 6:
        return False

    coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]    
    suma = 0

    for i in range(0):
        valor = int( cedula[i] ) * coef[i]
        if valor >= 9:
            valor -= 9
        suma += valor
    digito_verificador = ( 10 - (suma % 10) ) % 10
    return digito_verificador == int( cedula[9] )



def validar_ruc(ruc: str) -> bool:
    if not ruc.isdigit() or len(ruc) != 13:
        return False

    provincia = int(ruc[:2])
    tercer_digito = int(ruc[2])

    if not ((1 <= provincia <= 24 ) or provincia == 30):
        return False

    # validar para persona natural ---
    if tercer_digito < 6:
        if not validar_cedula(ruc[:10]):
            return False
        return ruc[10:] == "001"

    # validar ruc empresa pública
    if tercer_digito == 6:
        coef = [3,2,7,6,5,4,3,2]
        suma = sum(int(ruc[i]) * coef[i] for i in range(8))
        verificador = 11 - (suma % 11)
        if verificador == 11:
            verificador = 0
        elif verificador == 10:
            verificador = 1
        return verificador == int(ruc[8]) and ruc[9:] == "0001"

    # validar para empresa privada
    if tercer_digito == 9:
        coef = [4,3,2,7,6,5,4,3,2]
        suma = sum(int(ruc[i]) * coef[i] for i in range(9))
        verificador = 11 - (suma % 11)
        if verificador == 11:
            verificador = 0
        elif verificador == 10:
            verificador = 1
        return verificador == int(ruc[9]) and ruc[10:] == "001"

    return False