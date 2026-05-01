from django.urls import path
from . import views

app_name = 'bitacora'

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('salir/', views.logout_view, name='logout'),

    # Formularios (una URL por área)
    path('extrusion/', views.extrusion_view, name='extrusion'),
    path('impresion/', views.impresion_view, name='impresion'),
    path('conversion/', views.conversion_view, name='conversion'),

    # Historial
    path('historial/', views.historial_view, name='historial'),
    path('historial/<int:pk>/eliminar/', views.eliminar_registro_view, name='eliminar_registro'),

    # Gestión de usuarios (solo admin)
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('usuarios/registrar/', views.registrar_view, name='registrar'),
    path('usuarios/<int:pk>/toggle/', views.toggle_usuario_view, name='toggle_usuario'),
]
