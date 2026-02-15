from django.urls import path
from . import views

app_name = 'donantes'

urlpatterns = [
   path('', views.index, name='index'),
   path('crear/', views.crear_donante, name='crear_donante'),
   path('<int:id>/', views.detalle_donante, name='donante_detalle'),
   path('cambiar-estado/<int:id>/', views.toggle_estado_donante, name='toggle_estado'),
   path('editar/<int:id>/', views.editar_donante, name='editar_donante'),
]