from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, logout, authenticate
from .utils import validar_password
from .decorators import  role_required
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

# Vista paara realizar el login
def login_vista(request):
    errores = {}

    if request.method == 'POST':
        identificador = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not identificador or not password:
            errores['auth'] = "Ingrese usuario o cédula y contraseña"
            return render(request, 'auth/login.html', {'errores': errores})

        # Determinar si es cédula o username
        try:
            if identificador.isdigit():
                user_obj = Usuario.objects.get(cedula=identificador)
            else:
                user_obj = Usuario.objects.get(username=identificador)

            username_real = user_obj.username

        except Usuario.DoesNotExist:
            errores['auth'] = "Usuario o contraseña incorrectos"
            return render(request, 'auth/login.html', {'errores': errores})

        user = authenticate(request, username=username_real, password=password)

        if user is None:
            errores['auth'] = "Usuario o contraseña incorrectos"
            return render(request, 'auth/login.html', {'errores': errores})

        login(request, user)
        return redirect('dashboard:dashboard')

    return render(request, 'auth/login.html', {'errores': errores})


# Vista para ver listado de usuarios
@login_required
@role_required('ADMINISTRADOR')
def listar_usuarios(request):
    busqueda = request.GET.get('busqueda', '').strip()
    estado = request.GET.get('estado', 'ACTIVOS')

    usuarios = Usuario.objects.all()
    usuarios = usuarios.order_by('primer_apellido')
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(primer_nombre__icontains=busqueda) |
            Q(primer_apellido__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(cedula__icontains=busqueda)
        )

    if estado == 'ACTIVOS':
        usuarios = usuarios.filter(is_active=True)
    elif estado == 'INACTIVOS':
        usuarios = usuarios.filter(is_active=False)

    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'usuarios': page_obj,
        'busqueda': busqueda,
        'estado': estado,
    }
    return render(request, 'usuarios/index.html', context)
    

# vISTA PARA EDITAR USUARIOS - SOLO ADMIN
@login_required
@role_required('ADMINISTRADOR')
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    errores = {}

    if request.method == 'POST':
        data = request.POST

        # ===== Captura =====
        username = data.get('username', '').strip()
        primer_nombre = data.get('primer_nombre', '').strip()
        segundo_nombre = data.get('segundo_nombre', '').strip()
        primer_apellido = data.get('primer_apellido', '').strip()
        segundo_apellido = data.get('segundo_apellido', '').strip()
        cedula = data.get('cedula', '').strip()
        email = data.get('email', '').strip()
        telefono = data.get('telefono', '').strip()
        rol = data.get('rol')

        # ===== Validaciones =====
        if not username:
            errores['username'] = 'El usuario es obligatorio'
        elif Usuario.objects.exclude(id=usuario.id).filter(username=username).exists():
            errores['username'] = 'El nombre de usuario ya existe'

        if not primer_nombre:
            errores['primer_nombre'] = 'El primer nombre es obligatorio'

        if not primer_apellido:
            errores['primer_apellido'] = 'El primer apellido es obligatorio'

        if not cedula:
            errores['cedula'] = 'La cédula es obligatoria'
        elif Usuario.objects.exclude(id=usuario.id).filter(cedula=cedula).exists():
            errores['cedula'] = 'La cédula ya existe'

        if not email:
            errores['email'] = 'El correo es obligatorio'
        elif Usuario.objects.exclude(id=usuario.id).filter(email=email).exists():
            errores['email'] = 'El correo ya existe'

        if not rol:
            errores['rol'] = 'Debe seleccionar un rol'

        # ===== Guardar =====
        if not errores:
            usuario.username = username
            usuario.primer_nombre = primer_nombre
            usuario.segundo_nombre = segundo_nombre
            usuario.primer_apellido = primer_apellido
            usuario.segundo_apellido = segundo_apellido
            usuario.cedula = cedula
            usuario.email = email
            usuario.telefono = telefono
            usuario.rol = rol

            usuario.save()
            return redirect('usuarios:index')

    return render(request, 'usuarios/editar.html', {
        'usuario': usuario,
        'errores': errores
    })


@login_required
@role_required('ADMINISTRADOR')
def crear_usuario(request):

    errores = {}
    data = {}

    if request.method == 'POST':
        data = request.POST

        username = data.get('username', '').strip()
        primer_nombre = data.get('primer_nombre', '').strip()
        segundo_nombre = data.get('segundo_nombre', '').strip()
        primer_apellido = data.get('primer_apellido', '').strip()
        segundo_apellido = data.get('segundo_apellido', '').strip()
        cedula = data.get('cedula', '').strip()
        email = data.get('email', '').strip()
        telefono = data.get('telefono', '').strip()
        rol = data.get('rol', '').strip()
        password = data.get('password', '')
        password2 = data.get('password2', '')

        # ===== VALIDACIONES =====
        if not username:
            errores['username'] = 'El usuario es obligatorio'

        if not primer_nombre:
            errores['primer_nombre'] = 'El primer nombre es obligatorio'

        if not primer_apellido:
            errores['primer_apellido'] = 'El primer apellido es obligatorio'

        if not cedula:
            errores['cedula'] = 'La cédula es obligatoria'
        elif len(cedula) != 10:
            errores['cedula'] = 'La cédula debe tener 10 dígitos'

        if not email:
            errores['email'] = 'El correo es obligatorio'

        if not rol:
            errores['rol'] = 'Debe seleccionar un rol'

        if not password:
            errores['password'] = 'La contraseña es obligatoria'

        if password != password2:
            errores['password2'] = 'Las contraseñas no coinciden'

        # ===== SI HAY ERRORES =====
        if errores:
            return render(request, 'usuarios/crear.html', {
                'errores': errores,
                'data': data
            })

        # ===== CREAR USUARIO =====
        try:
            Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                primer_nombre=primer_nombre,
                segundo_nombre=segundo_nombre,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido,
                cedula=cedula,
                telefono=telefono,
                rol=rol,
                is_active=True
            )

            return redirect('usuarios:index')

        except IntegrityError:
            # validaciones específicos por campo
            if Usuario.objects.filter(username=username).exists():
                errores['username'] = 'Este usuario ya existe'

            if Usuario.objects.filter(email=email).exists():
                errores['email'] = 'Este correo ya está registrado'

            if Usuario.objects.filter(cedula=cedula).exists():
                errores['cedula'] = 'Esta cédula ya está registrada'

            return render(request, 'usuarios/crear.html', {
                'errores': errores,
                'data': data
            })

    return render(request, 'usuarios/crear.html')


@login_required
@role_required('ADMINISTRADOR')
def cambiar_estado_usuario(request, id):
    if request.method != 'POST':
        return redirect('usuarios:index')

    usuario = get_object_or_404(Usuario, id=id)

    # Evitar que un usuario se desactive a sí mismo
    if usuario.id != request.user.id:
            usuario.is_active = not usuario.is_active
            usuario.save()

    return redirect('usuarios:index')




@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def logout_vista(request):
    
    logout(request)

    return redirect('usuarios:login')



@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def perfil(request):
    usuario_id = request.user.id
    if not usuario_id:
        return redirect('usuarios:login')
    
    usuario = Usuario.objects.get(id=usuario_id)
    errores = {}
    
    if request.method == 'POST':
        data = request.POST
        
        # Validar email
        nuevo_email = data.get('email', '').strip()
        if nuevo_email:
            # Solo validar si el email cambió
            if nuevo_email != usuario.email:
                # Verificar si el email ya existe en otro usuario
                if Usuario.objects.filter(email=nuevo_email).exclude(id=usuario.id).exists():
                    errores['email'] = 'Este correo electrónico ya está registrado por otro usuario.'
        else:
            errores['email'] = 'El correo electrónico es obligatorio.'
        
        # Validar campos obligatorios
        if not data.get('primer_nombre', '').strip():
            errores['primer_nombre'] = 'El primer nombre es obligatorio.'
        
        if not data.get('primer_apellido', '').strip():
            errores['primer_apellido'] = 'El primer apellido es obligatorio.'
        
            
        # Si no hay errores, guardar
        if not errores:
            usuario.primer_nombre = data.get('primer_nombre', '').strip()
            usuario.segundo_nombre = data.get('segundo_nombre', '').strip()
            usuario.primer_apellido = data.get('primer_apellido', '').strip()
            usuario.segundo_apellido = data.get('segundo_apellido', '').strip()
            usuario.cedula = data.get('cedula', '').strip()
            usuario.email = nuevo_email
            usuario.telefono = data.get('telefono', '').strip()
            usuario.save()
            
            # Opcional: agregar mensaje de éxito
            return redirect('dashboard:dashboard')
    
    return render(request, 'usuarios/perfil.html', {
        'usuario': usuario,
        'errores': errores
    })


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def cambiar_password(request):
    usuario_id = request.user.id

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    if request.method == 'POST':
        actual = request.POST.get('actual')
        nueva1 = request.POST.get('nueva1')
        nueva2 = request.POST.get('nueva2')

        # Validar actual
        if not check_password(actual, usuario.password):
            return redirect('usuarios:cambiar_password')

        # Validar coincidencia
        if nueva1 != nueva2:
            return redirect('usuarios:cambiar_password')

        # Validar reglas personalizadas
        ok, msg = validar_password(nueva1)
        if not ok:
            return redirect('usuarios:cambiar_password')

        # Guardar nueva contraseña
        usuario.password = make_password(nueva1)
        usuario.save()

        return redirect('usuarios:perfil')

    return render(request, 'usuarios/cambiar_password.html', {
        'usuario': usuario
    })
