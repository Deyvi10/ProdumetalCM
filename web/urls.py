from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- RUTAS DE LA WEB PÚBLICA ---
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('servicios/', views.servicios, name='servicios'),
    path('proyectos/', views.proyectos, name='proyectos'),
    path('contacto/', views.contacto, name='contacto'),
    path('especialidad/<str:tipo>/', views.detalle_especialidad, name='detalle_especialidad'),
    path('proyecto/<str:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),

    # --- RUTAS DE ACCESO (LOGIN / LOGOUT) ---
    path('login/', auth_views.LoginView.as_view(template_name='web/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),

    # --- RUTAS DEL ERP INTERNO ---
    path('erp/dashboard/', views.dashboard_erp, name='dashboard_erp'),
    path('erp/nuevo-ticket/', views.crear_requerimiento, name='crear_requerimiento'),
    path('erp/ticket/<int:req_id>/materiales/', views.añadir_materiales, name='añadir_materiales'),
    path('erp/ticket/<int:req_id>/pdf/', views.imprimir_pdf_ticket, name='imprimir_pdf_ticket'),
    path('erp/empleados/', views.gestionar_empleados, name='gestionar_empleados'),
]