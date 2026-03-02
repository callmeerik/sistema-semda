from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Beneficiario, BeneficiarioParticular, BeneficiarioInstitucional
from django.db import transaction
from ..usuarios.decorators import role_required
from django.contrib.auth.decorators import login_required
import re
from config.utils import validar_cedula, validar_ruc


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def lista_beneficiarios(request):
    busqueda = request.GET.get('busqueda', '')
    tipo = request.GET.get('tipo', 'ALL')
    estado = request.GET.get('estado', 'ACTIVO')
    
    # obtener todos lops beneficiarios
    beneficiarios = Beneficiario.objects.select_related(
        'institucional',
        'particular'
    ).order_by('-id')

    busqueda_limpia = re.sub(r'\D', '', busqueda)

    filtros = Q()
    if busqueda:
        filtros = Q(email__icontains=busqueda) |\
        Q(particular__primer_nombre__icontains=busqueda) |\
        Q(particular__primer_apellido__icontains=busqueda) |\
        Q(institucional__nombre_institucion__icontains=busqueda)
            
   
        if busqueda_limpia:
            filtros |= Q(particular__cedula__icontains=busqueda_limpia)
            filtros |= Q(institucional__ruc__icontains=busqueda_limpia)
    beneficiarios = beneficiarios.filter(filtros)

    if tipo != "ALL":
        beneficiarios = beneficiarios.filter(tipo=tipo)
    
    if estado == 'ACTIVO':
        beneficiarios = beneficiarios.filter(is_active = True)
    elif estado == 'INACTIVO':
        beneficiarios = beneficiarios.filter(is_active = False)

    paginator = Paginator(beneficiarios, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "beneficiarios/index.html", {
        "beneficiarios": page_obj,
        'estado': estado,
        "busqueda": busqueda,
        "tipo": tipo,
        "total": paginator.count
    })


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def crear_beneficiario(request):

    errores = {}

    if request.method == "POST":

        tipo = request.POST.get("tipo")
        telefono = request.POST.get("telefono")
        direccion = request.POST.get("direccion")
        email = request.POST.get('email')

        if not tipo:
            errores["tipo"] = "Seleccione el tipo de beneficiario"

        if not errores:

            try:
                with transaction.atomic():

                    beneficiario = Beneficiario.objects.create(
                        tipo=tipo,
                        telefono=telefono,
                        direccion=direccion,
                        registrado_por=request.user
                    )

                    # 👤 PARTICULAR
                    if tipo == "PARTICULAR":

                        primer_nombre=request.POST.get("primer_nombre"),
                        segundo_nombre=request.POST.get("segundo_nombre"),
                        primer_apellido=request.POST.get("primer_apellido"),
                        segundo_apellido=request.POST.get("segundo_apellido"),
                        cedula=request.POST.get("cedula"),
                        sexo=request.POST.get('sexo'),
                        edad=request.POST.get("edad")

                        if not primer_nombre:
                            errores['primeer_nombre'] = "Este campo es obligatorio"
                        
                        if not primer_apellido:
                            errores['primer_apellido'] = "Este campo es obligatorio"

                        if not validar_cedula(cedula):
                            errores["cedula"] = "La cédula debe tener exactamente 10 dígitos."
                        elif BeneficiarioParticular.objects.filter(cedula=cedula).exists():
                            errores["cedula"] = "Ya existe un donante con esta cédula."
                        
                        if errores:
                            Beneficiario.delete()
                        else:
                            BeneficiarioParticular.objects.create(
                                beneficiario=beneficiario,
                                primer_nombre= primer_nombre,
                                segundo_nombre= segundo_nombre,
                                primer_apellido= primer_apellido,
                                segundo_apellido= segundo_apellido,
                                cedula= cedula,
                                sexo= sexo,                   
                                edad= edad
                            )
                            return redirect('beneficiarios:beneficiario_index')

                    # benef institucional
                    elif tipo == "INSTITUCIONAL":
                           
                        nombre_institucion=request.POST.get("nombre_institucion"),
                        tipo_institucion=request.POST.get("tipo_institucion"),
                        ruc=request.POST.get("ruc"),
                        nombre_representante=request.POST.get("nombre_representante"),
                        apellido_representante=request.POST.get("apellido_representante")
                        
                        if not nombre_institucion:
                            errores['nombre_institucion'] = 'Este camppo es obligatorio'
                        
                        if not tipo_institucion:
                            errores['tipo_institucion'] = 'Este camppo es obligatorio'
                        
                        if not validar_ruc(ruc):
                            errores["ruc"] = "El RUC debe tener 13 dígitos y terminar en 001."
                        elif BeneficiarioInstitucional.objects.filter(ruc=ruc).exists():
                            errores["ruc"] = "Ya existe un donante con este RUC."

                        if not nombre_institucion:
                            errores['nombre_rep'] = "Este campo es obligatorio"
                        
                        if not apellido_representante:
                            errores['apellodp_rep'] = "Este campo es obligatorio"
                        
                        if errores:
                            beneficiario.delete()
                        else:
                            BeneficiarioInstitucional.objects.create(
                                beneficiario=beneficiario,
                                nombre_institucion= nombre_institucion,
                                tipo_institucion= tipo_institucion,
                                ruc= ruc,
                                nombre_representante= nombre_representante,
                                apellido_representante= apellido_representante
                            )
                            return redirect('beneficiarios:beneficiario_index')
            except Exception as e:
                errores["general"] = str(e)

    return render(request, "beneficiarios/crear.html", {
        "errores": errores
    })


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def editar_beneficiario(request, id):

    beneficiario = get_object_or_404(
        Beneficiario,
        pk=id,
        is_active=True
    )

    errores = {}

    if request.method == "POST":

        beneficiario.telefono = request.POST.get("telefono")
        beneficiario.direccion = request.POST.get("direccion")
        beneficiario.email = request.POST.get('email')
        beneficiario.save()

        if beneficiario.tipo == "PARTICULAR":

            particular = beneficiario.particular
            particular.primer_nombre = request.POST.get("primer_nombre")
            particular.segundo_nombre = request.POST.get("segundo_nombre")
            particular.primer_apellido = request.POST.get("primer_apellido")
            particular.segundo_apellido = request.POST.get("segundo_apellido")
            particular.cedula = request.POST.get("cedula")
            particular.sexo=request.POST.get('sexo')
            particular.edad=request.POST.get('edad')
            particular.save()

        else:

            institucional = beneficiario.institucional
            institucional.nombre_institucion = request.POST.get("nombre_institucion")
            institucional.tipo_institucion = request.POST.get("tipo_institucion")
            institucional.ruc = request.POST.get("ruc")
            institucional.nombre_representante = request.POST.get("nombre_representante")
            institucional.apellido_representante = request.POST.get("apellido_representante")
            institucional.save()

        return redirect("beneficiarios:beneficiario_index")

    return render(request, "beneficiarios/editar.html", {
        "beneficiario": beneficiario,
        "errores": errores
    })

@login_required
@role_required('ADMINISTRADOR')
def eliminar_beneficiario(request, id):

    beneficiario = get_object_or_404(Beneficiario, pk=id)

    beneficiario.is_active = False
    beneficiario.save()

    return redirect("beneficiarios:beneficiario_index")



@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def beneficiario_detalle(request, id):
    beneficiario = get_object_or_404(
        Beneficiario.objects.select_related(
            'particular',
            'institucional',
            'registrado_por'
        ),
        id=id
    )

    return render(request, 'beneficiarios/detalle.html', {
        'beneficiario': beneficiario
    })
