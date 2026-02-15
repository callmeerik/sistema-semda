from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..usuarios.decorators import role_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Max
from django.shortcuts import render
from ..donaciones.models import Entrega
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from django.db.models import Q
from ..donaciones.models import Donacion
from ..donantes.models import Donante
import os


# vista para obtener los registros de entrega
# de cada casa hogar por fecha
@login_required
@role_required('ADMINISTRADOR')
def entregas_institucional(request):

    search = request.GET.get('busqueda', '').strip()

    queryset = (
        Entrega.objects
        .filter(
            estado='REALIZADA',
            beneficiario__tipo='INSTITUCIONAL'
        )
    )

    if search:
        queryset = queryset.filter(
            beneficiario__institucional__nombre_institucion__icontains=search
        )

    registros = (
        queryset
        .values(
            'beneficiario__id',
            'beneficiario__institucional__nombre_institucion',
            'beneficiario__institucional__tipo_institucion',
            'fecha_entrega'
        )
        .annotate(
            total_items=Sum('cantidad_entregada')
        )
        .order_by(
            'beneficiario__institucional__nombre_institucion',
            '-fecha_entrega'
        )
    )

    paginator = Paginator(registros, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'reportes/entregas_institucion.html',
        {
            'registros': page_obj,
            'search': search
        }
    )

@login_required
@role_required('ADMINISTRADOR')
def entregas_particular(request):

    search = request.GET.get('busqueda', '').strip()

    queryset = (
        Entrega.objects
        .filter(
            estado='REALIZADA',
            beneficiario__tipo='PARTICULAR'
        )
    )

    if search:
        queryset = queryset.filter(
            Q(beneficiario__particular__primer_nombre__icontains=search) |
            Q(beneficiario__particular__primer_apellido__icontains=search)
        )

    registros = (
        queryset
        .values(
            'beneficiario__id',
            'beneficiario__particular__primer_nombre',
            'beneficiario__particular__primer_apellido',
            'fecha_entrega'
        )
        .annotate(
            total_items=Sum('cantidad_entregada')
        )
        .order_by(
            'beneficiario__particular__primer_apellido',
            'beneficiario__particular__primer_nombre',
            '-fecha_entrega'
        )
    )

    paginator = Paginator(registros, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'reportes/entregas_particular.html',
        {
            'page_obj': page_obj,
            'search': search
        }
    )


@login_required
@role_required('ADMINISTRADOR')
def entregas_particular_fecha_pdf(request, id, fecha):

    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

    entregas = (
        Entrega.objects
        .filter(
            estado='REALIZADA',
            fecha_entrega=fecha,
            beneficiario__id=id,
            beneficiario__tipo='PARTICULAR'
        )
        .select_related(
            'beneficiario__particular',
            'item',
            'item__categoria'
        )
        .order_by('item__descripcion')
    )

    if not entregas.exists():
        return HttpResponse("No hay entregas para este reporte", status=404)

    particular = entregas.first().beneficiario.particular

    logo_ruta = os.path.join(
        settings.STATIC_ROOT,
        'images',
        'logo.png'
    )

    html_string = render_to_string(
        'reportes/entregas_particular_pdf.html',
        {
            'particular': particular,
            'fecha': fecha,
            'entregas': entregas,
            'logo_ruta':logo_ruta
        }
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="entregas_{particular.primer_apellido}_{fecha}.pdf"'
    )

    HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf(response)

    return response



@login_required
@role_required('ADMINISTRADOR')
def entregas_institucional_fecha_pdf(request, id, fecha):

    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

    entregas = (
        Entrega.objects
        .filter(
            estado='REALIZADA',
            fecha_entrega=fecha,
            beneficiario__id=id,
            beneficiario__tipo='INSTITUCIONAL'
        )
        .select_related(
            'beneficiario__institucional',
            'item',
            'item__categoria'
        )
        .order_by('item__descripcion')
    )

    if not entregas.exists():
        return HttpResponse("No hay entregas para este reporte", status=404)

    institucion = entregas.first().beneficiario.institucional

    logo_ruta = os.path.join(
        settings.STATIC_ROOT,
        'images',
        'logo.png'
    )

    html_string = render_to_string(
        'reportes/entregas_institucion_pdf.html',
        {
            'institucion': institucion,
            'fecha': fecha,
            'entregas': entregas,
            'logo_ruta':logo_ruta
        }
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="entregas_{institucion.nombre_institucion}_{fecha}.pdf"'
    )

    HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf(response)

    return response



# Reporte de doonantes y los items donados por cada uno
@login_required
@role_required('ADMINISTRADOR')
def donaciones_donante(request):
    search = request.GET.get('busqueda', '').strip()

    # query del join entre la tabla donantentes y donaciones
    donaciones = (
        Donacion.objects.select_related(
            'donante', 
            'donante__natural',
            'donante__juridico'
        )
    )

    if search:
        donaciones = donaciones.filter(
            Q(donante__natural__nombre__icontains=search) |
            Q(donante__natural__apellido__icontains=search) |
            Q(donante__juridico__razon_social__icontains=search) 
        )

    # agrupacion de datos para listado
    registros = (
        donaciones.values(
            'donante_id',
            'donante__natural__nombre',
            'donante__natural__apellido',
            'donante__juridico__razon_social',
            'descripcion',
            'fecha_donacion'
        )
        .annotate(
            total_donaciones = Count('items')
        ).filter(
            total_donaciones__gt=0
        ).order_by(
            'fecha_donacion',
            'donante_id'
        )
    )
    print(registros)

    paginator = Paginator(registros, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reportes/donaciones_donante.html', {
        'registros': page_obj,
        'search': search
    })


@login_required
@role_required('ADMINISTRADOR')
def donaciones_donante_fecha_pdf(request, id, fecha):

    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

    # join tabla base de donantes
    # y tablas de donante natural y juridico
    donante = Donante.objects.select_related(
        'natural',
        'juridico'
    ).get(id=id)

    # filtrar donaciones por donante y fecha
    donaciones = (
        Donacion.objects
        .filter(
            donante_id=id,
            fecha_donacion=fecha
        )
        .prefetch_related(
            'items',
            'items__categoria'
        )
        .order_by('-id')
    )
    
    if not donaciones.exists():
        return HttpResponse("No existen donaciones para este reporte", status=404)

    logo_ruta = os.path.join(
        settings.STATIC_ROOT,
        'images',
        'logo.png'
    )

    html_string = render_to_string(
        'reportes/donaciones_donante_pdf.html',
        {
            'donante': donante,
            'fecha': fecha,
            'donaciones': donaciones,
            'logo_ruta': logo_ruta
        }
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="donaciones_{donante.nombre_donante}_{fecha}.pdf"'
    )

    html = HTML(
        string=html_string,
        base_url=settings.BASE_DIR
    )
    pdf = html.write_pdf(response)

    return response


