from django.core.exceptions import ValidationError
from django.utils.timezone import now

# validacion de la fecha de entrega
def validar_fecha_entrega(value):
    if value < now().date():
        raise ValidationError("La fecha de entrega no puede ser anterior a la fecha actuañ")
