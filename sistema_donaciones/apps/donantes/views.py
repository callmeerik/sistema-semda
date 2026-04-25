from django.shortcuts import render, redirect, get_object_or_404
from .models import Donante, DonanteJuridico, DonanteNatural
from ..usuarios.decorators import role_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
import re 
from django.http import HttpResponseNotAllowed
from config.utils import validar_cedula, validar_ruc
from django.contrib.auth.decorators import login_required



@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def index(request):
    busqueda = request.GET.get('busqueda', '')
    tipo = request.GET.get('tipo', 'ALL')
    estado = request.GET.get('estado', 'ACTIVO')

    donantes = Donante.objects.select_related(
        'natural',
        'juridico'
    ).all().order_by('-id')

    if tipo in ['NATURAL', 'JURIDICO']:
        donantes = donantes.filter(tipo_donante=tipo)

    if estado == 'ACTIVO':
        donantes = donantes.filter(is_active=True)
    elif estado == 'INACTIVO':
        donantes = donantes.filter(is_active=False)
    
    

    filtros = Q()
    if busqueda:
        filtros = Q(natural__nombre__icontains=busqueda) |\
        Q(natural__apellido__icontains=busqueda) |\
        Q(juridico__razon_social__icontains=busqueda)
   
    donantes = donantes.filter(filtros).distinct()
    
    paginator = Paginator(donantes, 4)  # 8 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'donantes': page_obj,
        'busqueda': busqueda,
        'tipo': tipo,
        'estado': estado,
        'total': paginator.count,
        'page_obj': page_obj,
    }

    return render(request, 'donantes/index.html', context)


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def crear_donante(request):
    errores = {}
    data = {}

    if request.method == "POST":
        tipo = request.POST.get("tipo_donante")

        # datos comunes
        email = request.POST.get("email", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        direccion = request.POST.get("direccion", "").strip()

        data = request.POST

        # validaciones de campos del formulario
        if not tipo:
            errores["tipo_donante"] = "Seleccione el tipo de donante."

        if not email:
            errores["email"] = "El email es obligatorio."

        if not telefono:
            errores["telefono"] = "El teléfono es obligatorio."

        # si no hay errores comunes, creamos el donante base
        if not errores:
            donante = Donante.objects.create(
                tipo_donante=tipo,
                email=email,
                telefono=telefono,
                direccion=direccion,
                registrado_por=request.user,
                is_active=True
            )

            if tipo == "NATURAL":
                nombre = request.POST.get("nombre", "").strip()
                apellido = request.POST.get("apellido", "").strip()
                cedula = request.POST.get("cedula", "").strip()

                if not nombre:
                    errores["nombre"] = "El nombre es obligatorio."

                if not apellido:
                    errores["apellido"] = "El apellido es obligatorio."
                print(f"Cedula: {cedula}")
                print(cedula.isdigit())
                print(f"tipo: {type(cedula)}")
                print(validar_cedula(cedula))
                if not validar_cedula(cedula):
                    errores["cedula"] = "La cédula ingresada no es válida."
                elif DonanteNatural.objects.filter(cedula=cedula).exists():
                    errores["cedula"] = "Ya existe un donante con esta cédula."
                
                if errores:
                    donante.delete()
                else:
                    DonanteNatural.objects.create(
                        donante=donante,
                        nombre=nombre,
                        apellido=apellido,
                        cedula=cedula
                    )
                    return redirect("donantes:index")

            elif tipo == "JURIDICO":
                razon_social = request.POST.get("razon_social", "").strip()
                ruc = request.POST.get("ruc", "").strip()
                nombre_rep = request.POST.get("nombre_representante", "").strip()
                apellido_rep = request.POST.get("apellido_representante", "").strip()
                cargo_rep = request.POST.get("cargo_representante", "").strip()
               
                if not razon_social:
                    errores["razon_social"] = "La razón social es obligatoria."

                if not validar_ruc(ruc):
                    errores["ruc"] = "El RUC ingresado no es válido."
                elif DonanteJuridico.objects.filter(ruc=ruc).exists():
                    errores["ruc"] = "Ya existe un donante con este RUC."

                if not nombre_rep:
                    errores["nombre_representante"] = "El nombre del representante es obligatorio."

                if not apellido_rep:
                    errores["apellido_representante"] = "El apellido del representante es obligatorio."

                if errores:
                    donante.delete()
                else:
                    DonanteJuridico.objects.create(
                        donante=donante,
                        razon_social=razon_social,
                        ruc=ruc,
                        nombre_representante=nombre_rep,
                        apellido_representante=apellido_rep,
                        cargo_representante=cargo_rep
                    )
                    return redirect("donantes:index")

    return render(request, "donantes/crear.html", {
        "errores": errores,
        "data": data
    })


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def detalle_donante(request, id):
    donante = get_object_or_404(
        Donante.objects.select_related('natural', 'juridico'),
        pk=id
    )

    context = {
        'donante': donante
    }

    return render(request, 'donantes/detalle.html', context)



@login_required
@role_required('ADMINISTRADOR')
def toggle_estado_donante(request, id):
    if request.method == 'POST':
        donante = get_object_or_404(Donante, id=id)
        donante.is_active = not donante.is_active
        donante.save()
        return redirect('donantes:index')

    return HttpResponseNotAllowed(['POST'])


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def editar_donante(request, id):
    donante = get_object_or_404(Donante, id=id)
    errores = {}

    if request.user.rol == "ASISTENTE" and donante.registrado_por != request.user:
        messages.error(request,
                        'No puedes editar este donante',
                        extra_tags = 'error_edicion_donante')
        return redirect("donantes:index")        

    if request.method == 'POST':

        donante.email = request.POST.get('email', '').strip()
        donante.telefono = request.POST.get('telefono', '').strip()
        donante.direccion = request.POST.get('direccion', '').strip()

        if donante.tipo_donante == 'NATURAL':
            natural = donante.natural

            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            cedula = natural.cedula  # 🔒 NO se edita

            if not nombre:
                errores['nombre'] = 'El nombre es obligatorio'

            if not apellido:
                errores['apellido'] = 'El apellido es obligatorio'

            if len(cedula) != 10 or not cedula.isdigit():
                errores['cedula'] = 'La cédula debe tener 10 dígitos'

            if errores:
                return render(request, 'donantes/editar.html', {
                    'donante': donante,
                    'errores': errores
                })

            natural.nombre = nombre
            natural.apellido = apellido
            natural.save()

        else:
            juridico = donante.juridico

            razon_social = request.POST.get('razon_social', '').strip()
            nombre_rep = request.POST.get('nombre_representante', '').strip()
            apellido_rep = request.POST.get('apellido_representante', '').strip()
            cargo_rep = request.POST.get('cargo_representante', '').strip()
            ruc = juridico.ruc  #no se edita

            if not razon_social:
                errores['razon_social'] = 'La razón social es obligatoria'

            if not nombre_rep:
                errores['nombre_representante'] = 'El nombre del representante es obligatorio'

            if not apellido_rep:
                errores['apellido_representante'] = 'El apellido del representante es obligatorio'

            if len(ruc) != 13 or not ruc.isdigit() or not ruc.endswith('001'):
                errores['ruc'] = 'El RUC debe tener 13 dígitos y terminar en 001'

            if errores:
                return render(request, 'donantes/editar.html', {
                    'donante': donante,
                    'errores': errores
                })

            juridico.razon_social = razon_social
            juridico.nombre_representante = nombre_rep
            juridico.apellido_representante = apellido_rep
            juridico.cargo_representate = cargo_rep
            juridico.save()

        donante.save()
        return redirect('donantes:index')

    return render(request, 'donantes/editar.html', {
        'donante': donante
    })
