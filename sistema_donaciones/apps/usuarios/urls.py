from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.listar_usuarios, name='index'),
    path('crear/', views.crear_usuario, name='crear'),
    path('editar/<int:id>/', views.editar_usuario, name='editar'),
    path('cambiar-estado/<int:id>/', views.cambiar_estado_usuario, name='toggle_estado'),
    path('login/', views.login_vista, name='login' ),
    path('logout/', views.logout_vista, name='logout'),
    path('perfil/', views.perfil, name= 'perfil'),
    path('perfil/cambiar_password/', views.cambiar_password, name= 'cambiar_password'),

     path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='auth/password_reset.html',
            success_url=reverse_lazy('usuarios:password_reset_done')
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='auth/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='auth/password_reset_confirm.html',
            success_url=reverse_lazy('usuarios:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='auth/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]