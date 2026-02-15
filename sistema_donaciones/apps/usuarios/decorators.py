from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if not request.user:
                return redirect('usuarios:login')

            rol = request.user.rol

            if rol not in roles:
                return redirect('usuarios:login')  # crea esta vista si quieres
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
