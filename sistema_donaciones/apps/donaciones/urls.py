from django.urls import path
from . import views

app_name = 'donaciones'

urlpatterns = [
    path('', views.index_donaciones, name='index'),
    path('crear/', views.crear_donacion, name='crear'),
    path('editar/<int:id>', views.editar_donacion, name='editar'),
    path('detalle/<int:id>/', views.detalle_donacion, name='detalle'),
    
    #ITEMS
    path('items/agregar/<int:donacion_id>/', views.agregar_item_donacion, name='agregar_item'),
    path('items/editar/<int:id>/', views.editar_item_donacion, name='editar_item'),

    # CATEGORIAS
    path('categorias/', views.index_categorias, name='categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria' ),
    path('categorias/cambiar-estado/<int:id>/', views.toggle_estado_categoria, name='cambiar_estado_categoria'),
    
    # INVENTARIO
    path('inventario/', views.inventario_listado, name='inventario'),
    path('inventario/entregar/item/<int:id>', views.entregar_item,  name='entregar'),
    
    # ENTREGAS
    path('entregas/', views.index_entregas, name='entregas'),
    path('entragas/detalle/<int:id>/', views.entrega_detalle, name='entrega_detalle' ),
    path('entregas/anular-entrega/<int:id>/', views.anular_entrega, name='anular_entrega'),
    path('entregas/marcar-realizada/<int:id>/', views.marcar_entrega_realizada, name='entrega_realizada' ),
]