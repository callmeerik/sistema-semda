from django.shortcuts import render, redirect, get_object_or_404
from ..usuarios.decorators import role_required
from .models import Donacion, ItemDonacion, Categoria, Entrega, EntregaAnulada
from ..beneficiarios.models import Beneficiario
from django.db.models import Q, Count
from datetime import datetime, date
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator
from ..donantes.models import Donante
from ..beneficiarios.models import Beneficiario
from django.contrib.auth.decorators import login_required

# pagina principal de donaciones - filtros y listado
@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def index_donaciones(request):
    busqueda = request.GET.get('busqueda', '').strip()
    estado = request.GET.get('estado', '')

    donaciones_qs = Donacion.objects.select_related(
        'donante',
        'donante__natural',
        'donante__juridico'
    ).annotate(
        cantidad_items=Count('items')
    ).order_by('-fecha_donacion')

    #búsqueda
    if busqueda:
        donaciones_qs = donaciones_qs.filter(
            Q(donante__natural__nombre__icontains=busqueda) |
            Q(donante__natural__apellido__icontains=busqueda) |
            Q(donante__juridico__razon_social__icontains=busqueda)
        )

    # filtro por estado
    if estado:
        donaciones_qs = donaciones_qs.filter(estado=estado)

    paginator = Paginator(donaciones_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'donaciones': page_obj,
        'page_obj': page_obj,
        'busqueda': busqueda,
        'estado': estado,
        'total': paginator.count
    }

    return render(request, 'donaciones/index.html', context)





@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def crear_donacion(request):
    donantes = Donante.objects.filter(is_active=True).select_related('natural', 'juridico')

    errores = {}
    data = {}

    if request.method == 'POST':
        data = request.POST
        donante_id = data.get('donante')
        descripcion = data.get('descripcion')
        fecha_donacion = data.get('fecha_donacion')

        if not donante_id:
            errores['donante'] = 'Debe seleccionar un donante'

        try:
            fecha_donacion = date.fromisoformat(fecha_donacion)

            # validacion de años irreales
            if fecha_donacion.year < 2000 or fecha_donacion.year > date.today().year + 1:
                errores['fecha_donacion'] = 'Año de entrega no válido'

        except Exception:
            errores['fecha_donacion'] = 'Fecha inválida'


        if not errores:
            Donacion.objects.create(
                donante_id=donante_id,
                descripcion=descripcion,
                fecha_donacion = fecha_donacion,
                registrado_por = request.user,
                estado = 'ACTIVA'
            )
            return redirect('donaciones:index')

    context = {
        'donantes': donantes,
        'errores': errores
    }
    return render(request, 'donaciones/crear.html', context)


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def editar_donacion(request, id):
    donacion = get_object_or_404(Donacion, id=id)
    donantes = Donante.objects.filter(is_active=True)

    errores = {}

    if request.method == 'POST':
        data = request.POST
        donante_id = data.get('donante')
        fecha = data.get('fecha_donacion')
        descripcion = data.get('descripcion')

        if not donante_id:
            errores['donante'] = 'Debes seleccionar un donante'
        

        if not errores:
            donacion.donante_id = donante_id
            donacion.fecha_donacion = fecha
            donacion.descripcion = descripcion
            donacion.save()
            return redirect('donaciones:index')
    context = {
        'donacion': donacion,
        'donantes': donantes,
        'errores': errores
    }
    return render(request, 'donaciones/editar.html', context)


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def detalle_donacion(request, id):
    donacion = get_object_or_404(Donacion, id=id)

    items_donacion = ItemDonacion.objects.filter(
        donacion = donacion
    ).select_related('categoria')

    paginator = Paginator(items_donacion, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'donacion': donacion,
        'items': page_obj,
        'page_obj': page_obj
    }

    return render(request, 'donaciones/detalles.html', context)


# ----- Items o articulos donados 
@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def agregar_item_donacion(request, donacion_id):
    donacion = get_object_or_404(Donacion, id=donacion_id)

    # No permitir agregar items si la donación está completada
    if donacion.estado == 'COMPLETADA':
        return redirect('donaciones:detalle', donacion.id)

    categorias = Categoria.objects.filter(is_active=True)
    errores = {}

    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        descripcion = request.POST.get('descripcion')
        cantidad = request.POST.get('cantidad')
        unidad = request.POST.get('unidad_medida')
        fecha_vencimiento_str = request.POST.get('fecha_vencimiento') or None

        # VALIDACIONES
        if not categoria_id:
            errores['categoria'] = 'Seleccione una categoría'

        if not descripcion:
            errores['descripcion'] = 'La descripción es obligatoria'

        if not cantidad:
            errores['cantidad'] = 'La cantidad es obligatoria'
        else:
            try:
                cantidad = int(cantidad)
                if cantidad <= 0:
                    errores['cantidad'] = 'La cantidad debe ser mayor a 0'
            except ValueError:
                errores['cantidad'] = 'Cantidad inválida'

        if not unidad:
            errores['unidad'] = 'Seleccione una unidad de medida'
        
        # convertir fecha de vencimiento string a date
        fecha_vencimiento = None
        if fecha_vencimiento_str:
            fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()

        if not errores:
            ItemDonacion.objects.create(
                donacion=donacion,
                categoria_id=categoria_id,
                descripcion=descripcion,
                cantidad_total=cantidad,
                cantidad_disponible=cantidad,
                unidad_medida=unidad,
                fecha_vencimiento=fecha_vencimiento,
                registrado_por=request.user,
                estado='DISPONIBLE'
            )

            return redirect('donaciones:detalle', donacion.id)

    context = {
        'donacion': donacion,
        'categorias': categorias,
        'errores': errores
    }

    return render(request, 'inventario/agregar.html', context)





@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def editar_item_donacion(request, id):
    item = get_object_or_404(ItemDonacion, id=id) 
    error = {}
    
    if not item.es_editable:
        messages.error(request,
                        'No es posible editar, ya hay items entregados',
                        extra_tags = 'error_edicion_item')
        return redirect("donaciones:detalle", item.donacion.id)

    categorias = Categoria.objects.all()
    

    if request.method == "POST":
        descripcion = request.POST.get("descripcion", "").strip()
        cantidad_total_str = request.POST.get("cantidad_total")
        unidad_medida = request.POST.get("unidad_medida", "").strip()
        fecha_vencimiento_str = request.POST.get("fecha_vencimiento")
        categoria_id = request.POST.get("categoria")

        # VALIDACIONES
        if not descripcion:
            error["descripcion"] = "La descripción es obligatoria"

        # validación de la cantidad total donada
        # en caso de ser editada
        if not cantidad_total_str:
            error["cantidad_total"] = "La cantidad es obligatoria"
        else:
            cantidad_total = int(cantidad_total_str)
            entregado = item.cantidad_total - item.cantidad_disponible
            if cantidad_total < entregado:
                error["cantidad_total"] = f"No puede ser menor a lo ya entregado ({entregado})"

        # Procesar fecha de forma segura
        fecha_vencimiento = None
        if fecha_vencimiento_str:
            try:
                fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()
            except ValueError:
                error["fecha_vencimiento"] = "Formato de fecha inválido"

        if not error:
            # Calcular nueva disponibilidad basándose en lo que ya se entregó
            ya_entregado = item.cantidad_total - item.cantidad_disponible
            
            item.descripcion = descripcion
            item.cantidad_total = cantidad_total
            item.cantidad_disponible = cantidad_total - ya_entregado # Lo nuevo menos lo gastado
            item.unidad_medida = unidad_medida
            item.fecha_vencimiento = fecha_vencimiento
            item.categoria_id = categoria_id
            item.save()

            return redirect("donaciones:detalle", item.donacion.id)

    context = {
        "item": item,
        "categorias": categorias,
        "error": error
    }
    return render(request, "inventario/editar.html", context)



# Categorias de items donados
@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def index_categorias(request):
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'categorias/index.html', {
        'categorias': categorias
    })


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if nombre:
            Categoria.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                is_active=True
            )

    return redirect('donaciones:categorias')


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def toggle_estado_categoria(request, id):
    if request.method == 'POST':
        categoria = get_object_or_404(Categoria, id=id)
        categoria.is_active = not categoria.is_active
        categoria.save()

    return redirect('donaciones:categorias')




#----- Inventario - Items donados
@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def inventario_listado(request):
    busqueda = request.GET.get('busqueda', '').strip()
    estado = request.GET.get('estado', 'DISPONIBLE')

    items = ItemDonacion.objects.select_related(
        'categoria',
        'donacion',
        'donacion__donante'
    )

    if busqueda:
        items = items.filter(
            Q(descripcion__icontains=busqueda) |
            Q(donacion__donante__natural__nombre__icontains=busqueda) |
            Q(donacion__donante__natural__apellido__icontains=busqueda) |
            Q(donacion__donante__juridico__razon_social__icontains=busqueda)
        )

    if estado != 'ALL':
        items = items.filter(estado=estado)

    items = items.order_by('-id')

    paginator = Paginator(items, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventario/index.html', {
        'items': page_obj,
        'busqueda': busqueda,
        'estado': estado,
        'total': items.count()
    })



# Entregas

# pantalla de entregas
@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def index_entregas(request):
    busqueda = request.GET.get("busqueda", "").strip()
    estado = request.GET.get("estado", "ALL")

    entregas = Entrega.objects.select_related(
        "item",
        "beneficiario",
        "beneficiario__institucional",
        'beneficiario__particular',
        "registrada_por"
    ).order_by("-fecha_entrega", '-id')

    if busqueda:
        entregas = entregas.filter(
            Q(item__descripcion__icontains=busqueda) |
            Q(beneficiario__particular__primer_nombre__icontains=busqueda) |
            Q(beneficiario__particular__primer_apellido__icontains=busqueda) |
            Q(beneficiario__institucional__nombre_institucion__icontains=busqueda)
        )

    if estado != "ALL":
        entregas = entregas.filter(estado=estado)

    paginator = Paginator(entregas, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "entregas": page_obj,
        "busqueda": busqueda,
        "estado": estado,
        "total": paginator.count
    }

    return render(request, "entregas/index.html", context)



@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def entregar_item(request, id):

    item = get_object_or_404(
        ItemDonacion,
        id=id,
        estado='DISPONIBLE'
    )

    # Verificar vencimiento
    if item.fecha_vencimiento and item.fecha_vencimiento < date.today():
        item.estado = 'VENCIDO'
        item.save()
        return redirect('donaciones:inventario')

    # 🔹 Beneficiarios institucionales
    beneficiarios_institucionales = (
        Beneficiario.objects
        .filter(
            is_active=True,
            tipo='INSTITUCIONAL'
        )
        .select_related('institucional')
        .order_by('institucional__nombre_institucion')
    )

    # Beneficiarios particulares
    beneficiarios_particulares = (
        Beneficiario.objects
        .filter(
            is_active=True,
            tipo='PARTICULAR'
        )
        .select_related('particular')
        .order_by('particular__primer_apellido')
    )

    if request.method == 'POST':

        beneficiario_id = request.POST.get('beneficiario')
        cantidad = request.POST.get('cantidad')
        fecha_entrega = request.POST.get('fecha_entrega')
        recibida_por = request.POST.get('recibida_por')
        observaciones = request.POST.get('observaciones')

        errores = {}

        #  Validar beneficiario
        if not beneficiario_id:
            errores['beneficiario'] = 'Seleccione un beneficiario'

        #  Validar cantidad
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                errores['cantidad'] = 'La cantidad debe ser mayor a cero'
            elif cantidad > item.cantidad_disponible:
                errores['cantidad'] = 'No hay stock suficiente'
        except (TypeError, ValueError):
            errores['cantidad'] = 'Cantidad inválida'

        # Validar fecha
        try:
            fecha_entrega = date.fromisoformat(fecha_entrega)

            if fecha_entrega < date.today():
                errores['fecha_entrega'] = 'La fecha no puede ser menor a hoy'

            if fecha_entrega.year < 2000 or fecha_entrega.year > date.today().year + 1:
                errores['fecha_entrega'] = 'Año de entrega no válido'

        except Exception:
            errores['fecha_entrega'] = 'Fecha inválida'

        #  Validar quién recibe
        
        if errores:
            return render(request, 'inventario/entregar.html', {
                'item': item,
                'beneficiarios_institucionales': beneficiarios_institucionales,
                'beneficiarios_particulares': beneficiarios_particulares,
                'errores': errores,
                'data': request.POST,
                'today': date.today()
            })

        beneficiario = get_object_or_404(Beneficiario, id=beneficiario_id)

        # Crear entrega
        Entrega.objects.create(
            item=item,
            beneficiario=beneficiario,
            cantidad_entregada=cantidad,
            fecha_entrega=fecha_entrega,
            recibida_por=recibida_por,
            observaciones=observaciones,
            registrada_por=request.user,
            estado='REGISTRADA'
        )

        return redirect('donaciones:entregas')

    return render(request, 'inventario/entregar.html', {
        'item': item,
        'beneficiarios_institucionales': beneficiarios_institucionales,
        'beneficiarios_particulares': beneficiarios_particulares,
        'today': date.today()
    })



@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def marcar_entrega_realizada(request, id):
    entrega = get_object_or_404(Entrega, id=id)
    errores = {}

    # Solo entregas registradas
    if entrega.estado != 'REGISTRADA':
        errores['general'] = 'Solo las entregas registradas pueden marcarse como realizadas.'
        return render(request, 'entregas/index.html', {
            'entrega': entrega,
            'errores': errores
        })

    if request.method == 'POST':
        recibida_por = request.POST.get('recibida_por', '').strip()

        if not recibida_por:
            errores['recibida_por'] = 'Debe indicar quién recibe la entrega.'

        item = entrega.item

        if entrega.cantidad_entregada > item.cantidad_disponible:
            errores['cantidad'] = 'No hay stock suficiente para realizar esta entrega.'

        if not errores:
            with transaction.atomic():
                # descontar stock una vez realizada la entrega fisica
                item.cantidad_disponible -= entrega.cantidad_entregada
                item.save()  # recalcula DISPONIBLE o AGOTADO
                print("Disponible antes:", item.cantidad_disponible)
                print("Cantidad entregada:", entrega.cantidad_entregada)
                # marcar entrega
                entrega.recibida_por = recibida_por
                entrega.estado = 'REALIZADA'
                entrega.save()

            return redirect('donaciones:entrega_detalle', entrega.id)

    return render(request, 'entregas/index.html', {
        'entrega': entrega,
        'errores': errores
    })





@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def entrega_detalle(request, id):
    entrega = get_object_or_404(
        Entrega.objects.select_related(
            'item',
            'beneficiario',
            'beneficiario__particular',
            'beneficiario__institucional',
            'registrada_por'
        ),
        id=id
    )

    beneficiario = entrega.beneficiario

    datos_particular = None
    datos_institucional = None

    if beneficiario.tipo == 'PARTICULAR' and hasattr(beneficiario, 'particular'):
        datos_particular = beneficiario.particular

    if beneficiario.tipo == 'INSTITUCIONAL' and hasattr(beneficiario, 'institucional'):
        datos_institucional = beneficiario.institucional

    anulacion = None
    if entrega.estado == 'ANULADA' and hasattr(entrega, 'anulacion'):
        anulacion = entrega.anulacion

    return render(request, 'entregas/detalles.html', {
        'entrega': entrega,
        'beneficiario': beneficiario,
        'datos_particular': datos_particular,
        'datos_institucional': datos_institucional,
        'anulacion': anulacion
    })





@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def anular_entrega(request, id):
    entrega = get_object_or_404(Entrega, pk=id)
    errores = {}

    if request.method == "POST":
        # se debe ingresar el motivo de anulacion de entrega
        motivo = request.POST.get("motivo", "").strip()

        if entrega.estado == 'ANULADA':
            errores["general"] = "La entrega ya se encuentra anulada."

        if not motivo:
            errores["motivo"] = "Debe ingresar el motivo de la anulación."

        if not errores:
            with transaction.atomic():
                # registrar anulacion en la tabla respectiva
                EntregaAnulada.objects.create(
                    entrega=entrega,
                    motivo=motivo,
                    anulada_por=request.user
                )

                # cambio de estado a anulada
                entrega.estado = 'ANULADA'
                entrega.save()

            return redirect("donaciones:entregas")

    return render(request, "entregas/anular.html", {
        "entrega": entrega,
        "errores": errores
    })
