from django.db import models
from ..donantes.models import Donante
from ..beneficiarios.models import Beneficiario
from ..usuarios.models import Usuario
from .utils import validar_fecha_entrega
from django.db.models import Sum
from datetime import date

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nombre


class Donacion(models.Model):
    ESTADOS = (
        ('ACTIVA', 'Activa'),
        ('COMPLETADA', 'Completada')
    )
    id = models.BigAutoField(primary_key=True)
    donante = models.ForeignKey(
        Donante,
        on_delete=models.PROTECT,
        related_name='donaciones'
    )
    descripcion = models.TextField(blank=True, null=True)
    fecha_donacion = models.DateField(default=date.today)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='donaciones_registradas'
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='ACTIVA'
    )
    class Meta:
        db_table = 'donaciones'

    def __str__(self):
        return f"Donación #{self.id} - {self.donante}"


    def actualizar_estado(self):

        total_disponible = self.items.aggregate(
            total=Sum('cantidad_disponible')
        )['total'] or 0

        if total_disponible == 0:
            nuevo_estado = 'COMPLETADA'
        else:
            nuevo_estado = 'ACTIVA'

        if self.estado != nuevo_estado:
            self.estado = nuevo_estado
            self.save(update_fields=['estado'])



class ItemDonacion(models.Model):
    ESTADOS = (
        ('DISPONIBLE', 'Disponible'),
        ('AGOTADO', 'Agotado'),
        ('VENCIDO', 'Vencido'),
    )
    id = models.BigAutoField(primary_key=True)
    donacion = models.ForeignKey(
        Donacion,
        on_delete=models.CASCADE,
        related_name='items'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='items'
    )
    descripcion = models.CharField(max_length=200)
    cantidad_total = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()
    unidad_medida = models.CharField(max_length=20, default='unidad')
    fecha_vencimiento = models.DateField(blank=True, null=True)
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='DISPONIBLE'
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='items_registrados'
    )
    class Meta:
        db_table = 'items_donacion'

    @property
    def es_editable(self):
        # solo se edita si la cantidad total
        #  es igual a la disponible
        return self.cantidad_total == self.cantidad_disponible

    def save(self, *args, **kwargs):
        # Si es nuevo, inicializar disponible
        if not self.pk:
            self.cantidad_disponible = self.cantidad_total

        # Estado por vencimiento
        if self.fecha_vencimiento and self.fecha_vencimiento < date.today():
            self.estado = 'VENCIDO'
        # CAMBIO DE ESTADO DE ITEM SEGUN STOCK
        elif self.cantidad_disponible == 0:
            self.estado = 'AGOTADO'
        else:
            self.estado = 'DISPONIBLE'

        super().save(*args, **kwargs)
        self.donacion.actualizar_estado()




class Entrega(models.Model):
    ESTADOS = (
        ('REGISTRADA', 'Registrada'),
        ('REALIZADA', 'Realizada'),
        ('ANULADA', 'Anulada')
    )
    id = models.BigAutoField(primary_key=True)
    item = models.ForeignKey(
        ItemDonacion,
        on_delete=models.PROTECT,
        related_name='entregas'
    )
    beneficiario = models.ForeignKey(
        Beneficiario,
        on_delete=models.PROTECT,
        related_name='entregas'
    )
    cantidad_entregada = models.PositiveIntegerField(blank=False, null=False)
    fecha_entrega = models.DateField(validators=[validar_fecha_entrega], blank=False, null=False)
    recibida_por = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Persona que recibe físicamente la entrega"
    )
    registrada_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='entregas_registradas'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='REGISTRADA'
    )

    
    class Meta:
        db_table = 'entregas'

    def __str__(self):
        return f"Entrega #{self.id} - {self.item.descripcion}"




class EntregaAnulada(models.Model):
    id = models.BigAutoField(primary_key=True)
    entrega = models.OneToOneField(
        'Entrega',
        on_delete=models.CASCADE,
        related_name='anulacion'
    )

    motivo = models.TextField()
    anulada_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='anulaciones_entregas'
    )
    fecha_anulacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'entregas_anuladas'

    def __str__(self):
        return f"Entrega anulada: #{self.entrega.id}"
