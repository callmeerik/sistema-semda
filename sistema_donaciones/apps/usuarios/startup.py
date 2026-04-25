from django.db import OperationalError, ProgrammingError
from django.contrib.auth import get_user_model

def create_admin_if_not_exist():
    
    try:
        User = get_user_model()
        # COMPROBACION DE EXISTENCIA DE SUSPERUSUARIO
        if User.objects.filter(is_superuser = True).exists():
            return
        
        # CREACION SUPERUSUSARIO POR DEFAULT
        User.objects.create_superuser(
            username = 'admin',
            primer_nombre = 'Admin',
            primer_apellido = 'Sistema',
            cedula = '9999999999',
            email = "admin@semda.org",
            password = "adminSemda@21"
        )
        print("✅ Super usuario creado")
    except (OperationalError, ProgrammingError):
        print("❌ Base de datos no lista")
