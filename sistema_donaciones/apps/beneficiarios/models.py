from django.db import models
from ..usuarios.models import Usuario

class Beneficiario(models.Model):

    TIPO_BENEFICIARIO = [
        ('PARTICULAR', 'Particular'),
        ('INSTITUCIONAL', 'Institucional')
    ]
    id = models.BigAutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPO_BENEFICIARIO)

    # Datos generales
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=125, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='beneficiarios_registrados'
    )

    class Meta:
        db_table = 'beneficiarios'

class BeneficiarioParticular(models.Model):

    beneficiario = models.OneToOneField(
        Beneficiario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='particular'
    )

    primer_nombre = models.CharField(max_length=30, blank=False, null=False)
    segundo_nombre = models.CharField(max_length=30)
    primer_apellido = models.CharField(max_length=30, blank=False, null=False)
    segundo_apellido = models.CharField(max_length=30)
    cedula = models.CharField(max_length=10, unique=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    sexo = models.CharField(
            max_length=10,
            choices=[
                ('M', 'Masculino'),
                ('F', 'Femenino'),
                ('OTRO', 'Otro')
            ],
            blank=True,
            null=True
    )
    class Meta:
        db_table = 'beneficiarios_particulares'


class BeneficiarioInstitucional(models.Model):

    beneficiario = models.OneToOneField(
        Beneficiario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='institucional'
    )

    nombre_institucion = models.CharField(max_length=200)
    tipo_institucion = models.CharField(
        max_length=50,
        choices=[
            ('CASA_HOGAR', 'Casa Hogar'),
            ('FUNDACION', 'Fundación'),
            ('ASOCIACION', 'Asociación'),
            ('OTRO', 'Otro')
        ]
    )
    ruc = models.CharField(max_length=13, blank=False, null=False, unique=True)
    nombre_representante = models.CharField(max_length=30, blank=False, null=False )
    apellido_representante = models.CharField(max_length=30, blank=False, null=False)
    class Meta:
        db_table = 'beneficiarios_institucionales'


