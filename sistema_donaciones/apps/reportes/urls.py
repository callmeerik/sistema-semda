from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('entregas-casa-hogar/', views.entregas_institucional, 
         name='entregas_institucional_fecha'),

    path('entregas-insticucion/pdf/<int:id>/<str:fecha>/',
    views.entregas_institucional_fecha_pdf,
    name='entregas_institucional_fecha_pdf'),

     path('entregas-particular/', views.entregas_particular,
          name='entregas_particular'),

    path('entregas-particular/pdf/<int:id>/<str:fecha>/',
        views.entregas_particular_fecha_pdf,
        name='entregas_particular_fecha_pdf'),

    path('donaciones-donante/', views.donaciones_donante,
         name='donaciones_donante'),

    path('donacione-donante/pdf/<int:id>/<str:fecha>/',
         views.donaciones_donante_fecha_pdf,
         name='donaciones_donante_fecha_pdf'),
]