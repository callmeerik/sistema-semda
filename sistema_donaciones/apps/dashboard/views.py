from django.shortcuts import render
from ..usuarios.decorators import  role_required
from django.contrib.auth.decorators import login_required
from ..donaciones.models import Donacion, ItemDonacion, Categoria, Entrega, EntregaAnulada
from ..beneficiarios.models import Beneficiario
from datetime import date, timedelta
from django.db.models import Count, Sum
from django.db.models.functions import  TruncMonth


@login_required
@role_required('ADMINISTRADOR', 'ASISTENTE')
def dashboard(request):
    # metricas para tarjetas
    total_donaciones = Donacion.objects.count()
    total_inventario = ItemDonacion.objects.aggregate(
        total = Sum('cantidad_disponible')
    )['total'] or 0

    entregas_realizadas = Entrega.objects.filter(estado='REALIZADA').count()
    entregas_anuladas = Entrega.objects.filter(estado='ANULADA').count()
    total_beneficiarios = Beneficiario.objects.count()


    # graficos

    #grafico -> entrega por mes
    fecha_actual = date.today()
    hace_1_anio = fecha_actual - timedelta(365)

    entregas_mes = (
        Entrega.objects
            .filter(fecha_entrega__gte=hace_1_anio, estado='REALIZADA')
            .annotate(mes= TruncMonth('fecha_entrega'))
            .values('mes')
            .annotate(total= Count('id'))
            .order_by('mes')
    )
    entregas_mes_labels = []
    entregas_mes_values = []

    for entrega in entregas_mes:
        entregas_mes_labels.append(entrega['mes'].strftime('%b %Y'))
        entregas_mes_values.append(entrega['total'])


    # segundo grafico -> entregas por beneficiairo
    entregas_beneficiario = (
        Entrega.objects
        .values('beneficiario__tipo')
        .annotate(total=Sum('cantidad_entregada'))
        .order_by('-total')
    )
    categorias_labels = []
    categorias_values = []

    for entrega in entregas_beneficiario:
        categorias_labels.append(entrega['beneficiario__tipo'])
        categorias_values.append(entrega['total'])

     
    context = {
        'kpis': {
            'total_donaciones': total_donaciones,
            'total_items_inventario': total_inventario,
            'entregas_realizadas': entregas_realizadas,
            'entregas_anuladas': entregas_anuladas,
            'total_beneficiarios': total_beneficiarios,
        },
        'entregas_mes_labels': entregas_mes_labels,
        'entregas_mes_values': entregas_mes_values,
        'categorias_labels': categorias_labels,
        'categorias_values': categorias_values,
    }

    return render(request, 'dashboard/dashboard.html', context)