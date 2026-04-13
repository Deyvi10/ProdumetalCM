from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('servicios/', views.servicios, name='servicios'),
    path('proyectos/', views.proyectos, name='proyectos'),
    path('contacto/', views.contacto, name='contacto'),
    path('especialidad/<str:tipo>/', views.detalle_especialidad, name='detalle_especialidad'),
    path('proyecto/<str:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),

]