from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User, Group

# Importaciones de Modelos y Formularios
from .models import Requerimiento, Material, Proyecto
from .forms import RequerimientoForm, DetalleRequerimientoForm, RegistroEmpleadoForm


# =======================================================
# VISTAS DE LA PÁGINA WEB PÚBLICA
# =======================================================

def inicio(request):
    return render(request, 'web/inicio.html')

def nosotros(request):
    context = {
        'historia': "ProduMetal CM es una empresa dedicada a la gestión, diseño, fabricación y montaje de estructuras y carpintería metálica de alta calidad. Con 8 años de experiencia en estructuras metálicas y más de 20 años en carpintería metálica, nos hemos establecido como una opción confiable para proyectos residenciales, industriales y comerciales.",
        'mision': "Nos comprometemos a gestionar, diseñar y fabricar estructuras metálicas de alta calidad que superen las expectativas de nuestros clientes, garantizando la eficiencia, seguridad y sostenibilidad en cada proyecto.",
        'vision': "Ser una opción confiable para nuestros clientes en la fabricación de estructuras metálicas, mediante la innovación continua, la mejora de nuestros procesos y la entrega de soluciones de alta calidad."
    }
    return render(request, 'web/nosotros.html', context)

def servicios(request):
    lista_servicios = [
        {'titulo': 'Análisis y Diseño Estructural', 'desc': 'Cálculos precisos y seguridad.', 'img': 'serv_diseno.jpg'},
        {'titulo': 'Fabricación y Montaje', 'desc': 'Construcciones de gran envergadura.', 'img': 'serv_montaje.jpg'},
        {'titulo': 'Planos de Fabricación', 'desc': 'Detalles técnicos para taller.', 'img': 'serv_planos.jpg'},
        {'titulo': 'Control de Calidad', 'desc': 'Supervisión y dossier técnico.', 'img': 'serv_calidad.jpg'},
        {'titulo': 'Protección Anticorrosiva', 'desc': 'Pintura y galvanizado.', 'img': 'serv_pintura.jpg'},
        {'titulo': 'Soldadores Calificados', 'desc': 'Personal certificado AWS.', 'img': 'serv_soldadura.jpg'},
        {'titulo': 'Estructuras Metálicas', 'desc': 'Naves industriales optimizadas.', 'img': 'serv_galpon.jpg'},
        {'titulo': 'Techos y Cubiertas', 'desc': 'Galvalume y policarbonato.', 'img': 'serv_techo.jpg'},
        {'titulo': 'Losa Colaborante', 'desc': 'Instalación de Steel Deck.', 'img': 'serv_losa.jpg'},
        {'titulo': 'Gradas Metálicas', 'desc': 'Escaleras industriales y de lujo.', 'img': 'serv_grada.jpg'},
        {'titulo': 'Carpintería Metálica', 'desc': 'Puertas, rejas y pasamanos.', 'img': 'serv_puerta.jpg'},
    ]
    return render(request, 'web/servicios.html', {'servicios': lista_servicios})

def detalle_especialidad(request, tipo):
    datos = {
        'estructuras': {
            'titulo': 'Estructuras Metálicas',
            'desc_larga': 'Nos especializamos en el diseño, fabricación y montaje de estructuras de acero de alta complejidad. Desde naves industriales hasta edificios comerciales, garantizamos resistencia sísmica y durabilidad.',
            'galeria': ['est1.jpg', 'est2.jpg', 'est3.jpg', 'est4.jpg','est5.jpg','est6.jpg', 'est7.jpg', 'est8.jpg', 'est9.jpg']
        },
        'carpinteria': {
            'titulo': 'Carpintería Metálica',
            'desc_larga': 'El arte del metal aplicado a tu hogar o negocio. Creamos portones, pasamanos, rejas de seguridad y muebles con acabados finos y soldadura invisible donde se requiere.',
            'galeria': ['carp1.jpg', 'carp2.jpg', 'carp3.jpg', 'carp4.jpg', 'carp5.jpg']
        },
        'ingenieria': {
            'titulo': 'Ingeniería y Diseño',
            'desc_larga': 'Antes de soldar, calculamos. Nuestro departamento de ingeniería elabora planos de taller, memorias de cálculo y modelado 3D para asegurar que tu proyecto sea viable y seguro.',
            'galeria': ['ing1.jpg', 'ing2.jpg', 'ing3.jpg', 'ing4.jpg']
        }
    }
    
    info = datos.get(tipo)
    return render(request, 'web/detalle_especialidad.html', {'info': info})

def proyectos(request):
    lista_proyectos = [
        {'id': 'plaza-kocoa', 'titulo': 'Plaza Kocoa', 'categoria': 'Comercial / Estructuras', 'img': 'kocoa/kocoa_main.jpg'},
        {'id': 'campo-oh', 'titulo': 'Casa de Campo O&H', 'categoria': 'Residencial / Diseño', 'img': 'oh_main.jpg'},
        {'id': 'san-isidro', 'titulo': 'Conjunto San Isidro', 'categoria': 'Residencial / Carpintería', 'img': 'isidro_main.jpg'},
        {'id': 'vaca-lima', 'titulo': 'Residencia Vaca Lima', 'categoria': 'Residencial / Estructura Mixta', 'img': 'vaca_main.jpg'},
        {'id': 'residencia-art', 'titulo': 'Residencia Arteaga ', 'categoria': 'Residencial / Estructura Mixta', 'img': 'arteaga_main.jpg'}
    ]
    return render(request, 'web/proyectos.html', {'proyectos': lista_proyectos})

def detalle_proyecto(request, proyecto_id):
    datos_proyectos = {
        'plaza-kocoa': {
            'titulo': 'Plaza Kocoa',
            'ubicacion': 'Conocoto',
            'descripcion': 'Plaza Kocoa es un moderno proyecto comercial ubicado en Conocoto, diseñado para ofrecer espacios funcionales y una imagen arquitectónica contemporánea...',
            'fotos': ['kocoa/kocoa1.jpg', 'kocoa/kocoa2.jpg', 'kocoa/kocoa3.jpg', 'kocoa/kocoa4.jpg'],
            'videos': ['kocoa/kocoa_vid.mp4']
        },
        'campo-oh': {
            'titulo': 'Casa de Campo O&H',
            'ubicacion': 'Proyecto Residencial',
            'descripcion': 'Residencia O&H es un proyecto que integra la estructura metálica con principios geométricos...',
            'fotos': ['campo/campo1.jpg', 'campo/campo2.jpg', 'campo/campo3.jpg', 'campo/campo4.jpg', 'campo/campo5.jpg', 'campo/campo6.jpg', 'campo/campo7.jpg', 'campo/campo8.jpg', 'campo/campo9.jpg'],
            'videos': ['campo/campo_video1.mp4','campo/campo_video2.mp4']
        },
        'san-isidro': {
            'titulo': 'Conjunto de Casas San Isidro',
            'ubicacion': 'San Isidro',
            'descripcion': 'Un desarrollo residencial de primer nivel donde la carpintería y estructura metálica de ProduMetal CM aportan seguridad...',
            'fotos': ['conjunto/isidro1.jpg', 'conjunto/isidro2.jpg', 'conjunto/isidro3.jpg', 'conjunto/isidro4.jpg', 'conjunto/isidro5.jpg', 'conjunto/isidro6.jpg', 'conjunto/isidro7.jpg', 'conjunto/isidro8.jpg', 'conjunto/isidro9.jpg', 'conjunto/isidro10.jpg', 'conjunto/isidro11.jpg'],
            'videos': [] 
        },
        'vaca-lima': {
            'titulo': 'Residencia Vaca Lima',
            'ubicacion': 'Proyecto Residencial Privado',
            'descripcion': 'Vivienda de diseño exclusivo que fusiona la robustez del acero con acabados arquitectónicos de alta gama...',
            'fotos': ['vaca/vaca1.jpg', 'vaca/vaca2.jpg', 'vaca/vaca3.jpg', 'vaca/vaca4.jpg', 'vaca/vaca5.jpg', 'vaca/vaca6.jpg', 'vaca/vaca7.jpg', 'vaca/vaca8.jpg', 'vaca/vaca9.jpg', 'vaca/vaca10.jpg', 'vaca/vaca11.jpg', 'vaca/vaca12.jpg'],
            'videos': ['vaca/vaca_video1.mp4','vaca/vaca_video2.mp4','vaca/vaca_video3.mp4']
        },
        'residencia-art':{
            'titulo': 'Residencia Arteaga',
            'ubicacion': 'Proyecto Residencial Sangolquí',
            'descripcion': 'Proyecto de vivienda con estructura metálica portante de dos niveles, compuesta por columnas y vigas tipo IPE...',
            'fotos': ['arteaga/arteaga1.jpg', 'arteaga/arteaga2.jpg', 'arteaga/arteaga3.jpg', 'arteaga/arteaga4.jpg', 'arteaga/arteaga5.jpg', 'arteaga/arteaga6.jpg', 'arteaga/arteaga7.jpg', 'arteaga/arteaga8.jpg', 'arteaga/arteaga9.jpg', 'arteaga/arteaga10.jpg', 'arteaga/arteaga11.jpg', 'arteaga/arteaga12.jpg', 'arteaga/arteaga13.jpg', 'arteaga/arteaga14.jpg'],
            'videos': ['arteaga/arteaga_video1.mp4']
        }
    }

    proyecto = datos_proyectos.get(proyecto_id)
    return render(request, 'web/detalle_proyecto.html', {'p': proyecto})

def contacto(request):
    return render(request, 'web/contacto.html')



# =======================================================
# DEFINICIÓN DE ROLES (RBAC) -> Siempre van arriba del ERP
# =======================================================
def es_admin(user):
    return user.is_superuser

def es_solicitante(user):
    return user.groups.filter(name='Solicitante').exists() or user.is_superuser

def es_bodeguero(user):
    return user.groups.filter(name='Bodeguero').exists() or user.is_superuser



# =======================================================
# VISTAS DEL SISTEMA ERP (INTERNO)
# =======================================================

@login_required(login_url='login')
def dashboard_erp(request):
    mis_requerimientos = Requerimiento.objects.filter(solicitante=request.user).order_by('-fecha_solicitud')
    context = {
        'requerimientos': mis_requerimientos
    }
    return render(request, 'web/erp/dashboard.html', context)

@login_required(login_url='login')
@user_passes_test(es_solicitante, login_url='dashboard_erp')
def crear_requerimiento(request):
    if request.method == 'POST':
        form_req = RequerimientoForm(request.POST)
        if form_req.is_valid():
            nuevo_req = form_req.save(commit=False)
            nuevo_req.solicitante = request.user 
            nuevo_req.save() 
            
            messages.success(request, f'Ticket {nuevo_req.folio} creado con éxito. Ahora añade los materiales.')
            return redirect('añadir_materiales', req_id=nuevo_req.id)
    else:
        form_req = RequerimientoForm()

    return render(request, 'web/erp/crear_requerimiento.html', {'form': form_req})

@login_required(login_url='login')
@user_passes_test(es_solicitante, login_url='dashboard_erp')
def añadir_materiales(request, req_id):
    requerimiento = get_object_or_404(Requerimiento, id=req_id, solicitante=request.user)
    detalles = requerimiento.detalles.all() 

    if request.method == 'POST':
        form_detalle = DetalleRequerimientoForm(request.POST)
        if form_detalle.is_valid():
            nuevo_detalle = form_detalle.save(commit=False)
            nuevo_detalle.requerimiento = requerimiento
            nuevo_detalle.save()
            messages.success(request, 'Material añadido al ticket.')
            return redirect('añadir_materiales', req_id=requerimiento.id)
    else:
        form_detalle = DetalleRequerimientoForm()

    context = {
        'requerimiento': requerimiento,
        'detalles': detalles,
        'form': form_detalle
    }
    return render(request, 'web/erp/añadir_materiales.html', context)


# --- VISTA EXCLUSIVA PARA EL DUEÑO ---
@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def gestionar_empleados(request):
    # Truco: Creamos los roles automáticamente si no existen en la BD
    Group.objects.get_or_create(name='Bodeguero')
    Group.objects.get_or_create(name='Solicitante')

    # Traemos a todos los empleados que no sean el dueño
    empleados = User.objects.filter(is_superuser=False).order_by('-date_joined')

    if request.method == 'POST':
        form = RegistroEmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado registrado y rol asignado correctamente.')
            return redirect('gestionar_empleados')
        else:
            messages.error(request, 'Hubo un error. Revisa que el usuario no exista ya.')
    else:
        form = RegistroEmpleadoForm()

    return render(request, 'web/erp/gestionar_empleados.html', {'form': form, 'empleados': empleados})