from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from fernet_fields import EncryptedCharField, EncryptedTextField

# Modelo Usuario Administrador personalizado
class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('El username es obligatorio')
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hashea la contraseña automáticamente
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('rol', 'ADMINISTRADOR')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


# Modelo de Usuario
class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, blank=False, null=False)
    primer_nombre = models.CharField(max_length=30, blank=False, null=False)
    segundo_nombre = models.CharField(max_length=30, blank=True, null=True)
    primer_apellido = models.CharField(max_length=30, blank=False, null=False)
    segundo_apellido = models.CharField(max_length=30, blank=True, null=True)
    cedula = EncryptedCharField(max_length=10, unique=True, blank=True, null=True)
    email = EncryptedCharField(max_length=100, blank=False, null=False, unique=True)
    telefono = EncryptedCharField(max_length=20, blank=False, null=False)
    rol = models.CharField(
        max_length=20, 
        choices=[('ADMINISTRADOR','ADMINISTRADOR'), 
                 ('ASISTENTE','ASISTENTE')],
        default='ASISTENTE'
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UsuarioManager()

    # Login con username
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'primer_nombre', 'primer_apellido', 'cedula']

    def __str__(self):
        return self.username

    def get_full_name(self):
        return " ".join(filter(None, [
            self.primer_nombre,
            self.segundo_nombre,
            self.primer_apellido,
            self.segundo_apellido
        ]))

    class Meta:
        db_table = 'usuarios'  # Nombre exacto de la tabla en la DB
