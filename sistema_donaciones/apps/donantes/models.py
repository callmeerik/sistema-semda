from django.db import models
from ..usuarios.models import Usuario
from fernet_fields import EncryptedCharField, EncryptedTextField

class Donante(models.Model):
    TIPO_DONANTE = [
        ('NATURAL', 'Natural'),
        ('JURIDICO', 'Juridico')
    ]
    id = models.BigAutoField(primary_key=True)
    tipo_donante = models.CharField(
        max_length= 10,
        choices= TIPO_DONANTE
    )
    email = EncryptedCharField(max_length=120, blank=False, null=False)
    telefono = EncryptedCharField(max_length=15, blank=True, null=True)
    direccion = EncryptedTextField(blank=False, null=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='donantes_registradas'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'donantes'

    def nombre_donante(self):
        if self.tipo_donante == 'NATURAL' and hasattr(self, 'natural'):
            return f"{self.natural.nombre} {self.natural.apellido}"
        if self.tipo_donante == 'JURIDICO' and hasattr(self, 'juridico'):
            return self.juridico.razon_social
        return self.email
    
    

    def __str__(self):
        return self.nombre_donante()
    

class DonanteNatural(models.Model):
    donante = models.OneToOneField(
        Donante,
        on_delete= models.CASCADE,
        primary_key= True,
        related_name= 'natural'
    )
    nombre = models.CharField(max_length=30, blank=False, null=False)
    apellido = models.CharField(max_length=30, blank=False, null=False)
    cedula = EncryptedCharField(max_length=10, blank=False, null=False, unique=True)

    class Meta:
        db_table = 'donantes_naturals'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    

class DonanteJuridico(models.Model):
    donante = models.OneToOneField(
        Donante,
        on_delete= models.CASCADE,
        primary_key= True,
        related_name= 'juridico'
    )
    razon_social = models.CharField(max_length=200, blank=False, null=False)
    ruc = EncryptedCharField(max_length=13, blank=False, null=False, unique=True)
    nombre_representante = models.CharField(max_length=30, blank=False, null=False )
    apellido_representante = models.CharField(max_length=30, blank=False, null=False)
    cargo_representante = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        db_table = 'donantes_juridicos'
    
    def __str__(self):
        return self.razon_social