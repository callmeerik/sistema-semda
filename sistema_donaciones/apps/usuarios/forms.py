from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from .utils import validar_password

class CustomSetPasswordForm(SetPasswordForm):

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")

        valido, mensaje = validar_password(password)
        if not valido:
            raise ValidationError(mensaje)

        return password