
from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('perfil/', views.seleccionar_perfil, name='seleccionar_perfil'),
    path('acceso/<str:rol>/', views.elegir_acceso, name='elegir_acceso'),

    path('registro/', views.registro, name='registro'),
    path('iniciar-sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),

    path('jugador/', views.jugador, name='jugador'),
    path('entrenador/', views.entrenador, name='entrenador'),
    path('administrador/', views.administrador, name='administrador'),

    path('torneos/', views.torneos, name='torneos'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('calendario/', views.calendario, name='calendario'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('resultados/', views.resultados, name='resultados'),
    path('chat/', views.chat, name='chat'),
    path('equipos/', views.equipos, name='equipos'),
]
