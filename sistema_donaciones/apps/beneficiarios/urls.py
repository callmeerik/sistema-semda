from django.urls import path
from . import views

app_name = 'beneficiarios'

urlpatterns = [
    path('', views.lista_beneficiarios, name='beneficiario_index'),
    path('crear/', views.crear_beneficiario, name='beneficiario_crear'),
    path('editar/<int:id>', views.editar_beneficiario, name='beneficiario_editar'),
    path('cambiar-estado/<int:id>', views.eliminar_beneficiario, name='beneficiario_cambiar_estado'),
    path('beneficiarios/<int:id>/', 
     views.beneficiario_detalle, 
     name='beneficiario_detalle'),

]