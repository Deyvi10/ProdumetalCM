from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.db.models import F
from axes.models import AccessAttempt
from django.db import transaction
from django.core.paginator import Paginator

# =======================================================
# IMPORTACIONES DE MODELOS Y FORMULARIOS (CORREGIDO)
# =======================================================
from .models import (
    Requerimiento, DetalleRequerimiento, Material, Proyecto, MovimientoInventario, 
    OrdenCompra, DetalleOrdenCompra, SolicitudCompra, CotizacionItem
)
from .forms import (
    RequerimientoForm, DetalleRequerimientoForm, RegistroEmpleadoForm, 
    ProyectoForm, OrdenCompraForm, DetalleOrdenCompraForm, AjusteInventarioForm
)

# NUEVOS IMPORTS PARA GENERACIÓN DE PDF
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import os
from django.conf import settings
from django.utils import timezone


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
    # (El contenido de detalle_proyecto se mantiene igual)
    datos_proyectos = {
        'plaza-kocoa': {
            'titulo': 'Plaza Kocoa',
            'ubicacion': 'Conocoto',
            'descripcion': 'Plaza Kocoa es un moderno proyecto comercial ubicado en Conocoto, diseñado para ofrecer espacios funcionales...',
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

def es_comprador(user):
    return user.groups.filter(name='Compras').exists() or user.is_superuser


# =======================================================
# VISTAS DEL SISTEMA ERP (INTERNO)
# =======================================================

@login_required(login_url='login')
def dashboard_erp(request):
    usuario = request.user
    context = {}

    # 1. VISTA DEL DUEÑO / ADMINISTRADOR
    if es_admin(usuario):
        context['rol'] = 'Administrador'
        context['tickets_pendientes'] = Requerimiento.objects.filter(estado='PENDIENTE').order_by('fecha_solicitud')
        context['ultimos_movimientos'] = MovimientoInventario.objects.all().order_by('-fecha_hora')[:5]
        context['cotizaciones_pendientes'] = SolicitudCompra.objects.filter(estado='COTIZADO').order_by('fecha_creacion')
        
    # 2. VISTA DEL BODEGUERO
    elif es_bodeguero(usuario):
        context['rol'] = 'Bodeguero'
        context['tickets_por_despachar'] = Requerimiento.objects.filter(estado='APROBADO')
        context['mis_compras_pendientes'] = OrdenCompra.objects.filter(estado='BORRADOR')
        context['alertas_stock'] = Material.objects.filter(stock_actual__lte=F('stock_minimo'))

    # 3. VISTA DEL DEPARTAMENTO DE COMPRAS
    elif es_comprador(usuario):
        context['rol'] = 'Compras'
        context['solicitudes_compras'] = SolicitudCompra.objects.filter(estado='ENVIADO_A_COMPRAS').order_by('-fecha_creacion')

    # 4. VISTA DEL SOLICITANTE / TÉCNICO
    else:
        context['rol'] = 'Solicitante'
        context['mis_requerimientos'] = Requerimiento.objects.filter(solicitante=usuario).order_by('-fecha_solicitud')

    return render(request, 'web/erp/dashboard.html', context)


# --- GESTIÓN DE REQUERIMIENTOS (SOLICITANTES) ---

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


# --- VISTA DE APROBACIÓN DE TICKETS (Solo Administrador) ---
@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def procesar_ticket(request, req_id, accion):
    ticket = get_object_or_404(Requerimiento, id=req_id)
    
    if accion == 'aprobar':
        ticket.estado = 'APROBADO'
        messages.success(request, f"Ticket {ticket.folio} aprobado para despacho en bodega.")
        
    elif accion == 'rechazar':
        ticket.estado = 'RECHAZADO'
        messages.warning(request, f"Ticket {ticket.folio} ha sido rechazado.")
        
    elif accion == 'compras':
        # NUEVO: Enviar automáticamente a Compras y empaquetar los materiales
        ticket.estado = 'EN_COMPRAS'
        solicitud, created = SolicitudCompra.objects.get_or_create(
            requerimiento_origen=ticket,
            defaults={'estado': 'ENVIADO_A_COMPRAS'}
        )
        if created:
            for detalle in ticket.detalles.all():
                CotizacionItem.objects.create(
                    solicitud=solicitud,
                    material=detalle.material,
                    cantidad_requerida=detalle.cantidad_solicitada
                )
        messages.info(request, f"Ticket {ticket.folio} enviado al departamento de Compras para cotización.")
    
    ticket.save()
    return redirect('dashboard_erp')


# =======================================================
# MÓDULO DE COMPRAS Y COTIZACIONES (NUEVO FLUJO)
# =======================================================

@login_required(login_url='login')
@user_passes_test(es_comprador, login_url='dashboard_erp')
def atender_cotizacion(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudCompra, id=solicitud_id)
    items = solicitud.items_cotizados.all()
    
    if request.method == 'POST':
        # Recorremos cada ítem para guardar los precios que puso Compras
        for item in items:
            proveedor = request.POST.get(f'proveedor_{item.id}')
            precio = request.POST.get(f'precio_{item.id}')
            especificaciones = request.POST.get(f'especificaciones_{item.id}')
            certificado = request.POST.get(f'certificado_{item.id}') == 'on'

            if proveedor and precio:
                item.proveedor_cotizado = proveedor
                item.precio_unitario = precio
                item.especificaciones_tecnicas = especificaciones
                item.certificado_calidad_incluido = certificado
                item.save()

        solicitud.estado = 'COTIZADO'
        solicitud.save()
        messages.success(request, f"Cotización {solicitud.folio} enviada al Administrador para su aprobación.")
        return redirect('dashboard_erp')
        
    return render(request, 'web/erp/atender_cotizacion.html', {'solicitud': solicitud, 'items': items})


@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def revisar_cotizacion(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudCompra, id=solicitud_id)
    items = solicitud.items_cotizados.all()
    
    if request.method == 'POST':
        # El Admin aprueba o rechaza cada ítem
        for item in items:
            estado = request.POST.get(f'estado_{item.id}')
            motivo = request.POST.get(f'motivo_{item.id}', '')

            if estado in ['APROBADO', 'RECHAZADO']:
                item.estado_aprobacion = estado
                if estado == 'RECHAZADO':
                    item.motivo_rechazo = motivo
                item.save()

        # Una vez guardado todo, llamamos a la función mágica que crea las órdenes de compra
        return redirect('finalizar_revision_cotizacion', solicitud_id=solicitud.id)
        
    return render(request, 'web/erp/revisar_cotizacion.html', {'solicitud': solicitud, 'items': items})

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
@transaction.atomic
def finalizar_revision_cotizacion(request, solicitud_id):
    # Paso Final: Generar Órdenes de Compra para Bodega automáticamente
    solicitud = get_object_or_404(SolicitudCompra, id=solicitud_id)
    items_aprobados = solicitud.items_cotizados.filter(estado_aprobacion='APROBADO')
    
    # Agrupamos por proveedor
    proveedores = items_aprobados.values_list('proveedor_cotizado', flat=True).distinct()
    
    for prov in proveedores:
        if prov: # Asegurarnos que hay un proveedor registrado
            items_prov = items_aprobados.filter(proveedor_cotizado=prov)
            
            nueva_oc = OrdenCompra.objects.create(
                proveedor=prov,
                creado_por=request.user,
                estado='EMITIDA', 
                observaciones=f"Generada automáticamente desde Solicitud {solicitud.folio}"
            )
            
            for item in items_prov:
                DetalleOrdenCompra.objects.create(
                    orden=nueva_oc,
                    material=item.material,
                    cantidad_pedida=item.cantidad_requerida
                )
            
    solicitud.estado = 'PROCESADO'
    solicitud.save()
    messages.success(request, "Órdenes de compra generadas y enviadas a Bodega correctamente.")
    return redirect('dashboard_erp')


# =======================================================
# MÓDULO DE INVENTARIO Y ABASTECIMIENTO TRADICIONAL
# =======================================================

@login_required(login_url='login')
@user_passes_test(lambda u: es_bodeguero(u) or es_admin(u), login_url='dashboard_erp')
def crear_orden_compra(request):
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST, request.FILES)
        if form.is_valid():
            nueva_oc = form.save(commit=False)
            nueva_oc.creado_por = request.user
            nueva_oc.save()
            return redirect('añadir_items_oc', oc_id=nueva_oc.id)
    else:
        form = OrdenCompraForm()
    return render(request, 'web/erp/crear_oc.html', {'form': form})

@login_required(login_url='login')
@user_passes_test(lambda u: es_bodeguero(u) or es_admin(u), login_url='dashboard_erp')
def añadir_items_oc(request, oc_id):
    oc = get_object_or_404(OrdenCompra, id=oc_id)
    detalles = oc.detalles.all()

    if request.method == 'POST':
        form_detalle = DetalleOrdenCompraForm(request.POST)
        if form_detalle.is_valid():
            material = form_detalle.cleaned_data['material']
            item_existente = detalles.filter(material=material).first()
            if item_existente:
                item_existente.cantidad_pedida += form_detalle.cleaned_data['cantidad_pedida']
                item_existente.save()
            else:
                nuevo_item = form_detalle.save(commit=False)
                nuevo_item.orden = oc
                nuevo_item.save()
            
            messages.success(request, f'Se añadió {material.nombre} a la orden.')
            return redirect('añadir_items_oc', oc_id=oc.id)
    else:
        form_detalle = DetalleOrdenCompraForm()

    return render(request, 'web/erp/añadir_items_oc.html', {
        'oc': oc, 'detalles': detalles, 'form': form_detalle
    })

@login_required(login_url='login')
@user_passes_test(lambda u: es_bodeguero(u) or es_admin(u), login_url='dashboard_erp')
def listar_ordenes_compra(request):
    es_administrador = es_admin(request.user)
    
    if es_administrador:
        ordenes = OrdenCompra.objects.all().order_by('-fecha_creacion')
        estados_permitidos = OrdenCompra.ESTADOS
    else:
        ordenes = OrdenCompra.objects.exclude(estado='BORRADOR').order_by('-fecha_creacion')
        estados_permitidos = [est for est in OrdenCompra.ESTADOS if est[0] != 'BORRADOR']

    estado = request.GET.get('estado')
    if estado:
        ordenes = ordenes.filter(estado=estado)

    return render(request, 'web/erp/listar_oc.html', {
        'ordenes': ordenes,
        'estados': estados_permitidos, 
        'estado_filtro': estado,
        'rol': 'Administrador' if es_administrador else 'Bodeguero',
    })

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def aprobar_oc(request, oc_id):
    oc = get_object_or_404(OrdenCompra, id=oc_id)
    if oc.estado == 'BORRADOR':
        oc.estado = 'EMITIDA' 
        oc.save()
        messages.success(request, f"¡Orden de Compra {oc.folio} APROBADA! El bodeguero ya puede verla para recibir el stock.")
    return redirect('listar_ordenes_compra')

@login_required(login_url='login')
@user_passes_test(lambda u: es_bodeguero(u) or es_admin(u), login_url='dashboard_erp')
def recibir_orden_compra(request, oc_id):
    oc = get_object_or_404(OrdenCompra, id=oc_id)
    if oc.estado == 'EMITIDA': 
        detalles = oc.detalles.all()
        for item in detalles:
            material = item.material
            material.stock_actual += item.cantidad_pedida
            material.save()

            MovimientoInventario.objects.create(
                material=material, tipo='INGRESO', cantidad=item.cantidad_pedida,
                responsable=request.user, orden_compra_asociada=oc, certificado_calidad=oc.documento_respaldo
            )
        
        oc.estado = 'RECIBIDA'
        oc.save()
        messages.success(request, f"Orden {oc.folio} recibida. Stock actualizado correctamente.")
    
    return redirect('listar_ordenes_compra')

@login_required(login_url='login')
@user_passes_test(lambda u: es_bodeguero(u) or es_admin(u), login_url='dashboard_erp')
def inventario_actual(request):
    materiales = Material.objects.filter(is_active=True).order_by('tipo', 'nombre')
    alertas = Material.objects.filter(is_active=True, stock_actual__lte=F('stock_minimo'))

    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro in ['MATERIAL', 'CONSUMIBLE']:
        materiales = materiales.filter(tipo=tipo_filtro)
        
    alerta_filtro = request.GET.get('alerta')
    if alerta_filtro == '1':
        materiales = materiales.filter(stock_actual__lte=F('stock_minimo'))

    rol_actual = 'Administrador' if es_admin(request.user) else 'Bodeguero'

    return render(request, 'web/erp/inventario.html', {
        'materiales': materiales,
        'alertas': alertas,
        'rol': rol_actual,
    })

@login_required(login_url='login')
@user_passes_test(es_bodeguero, login_url='dashboard_erp')
def crear_material(request):
    from .forms import MaterialForm
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material añadido al catálogo correctamente.')
            return redirect('inventario_actual')
    else:
        form = MaterialForm()
    return render(request, 'web/erp/crear_material.html', {'form': form})

@login_required(login_url='login')
@user_passes_test(lambda u: es_bodeguero(u) or es_admin(u), login_url='dashboard_erp')
def editar_material(request, material_id):
    from .forms import MaterialForm 
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Material {material.sku} actualizado correctamente!')
            return redirect('inventario_actual')
    else:
        form = MaterialForm(instance=material)
        
    return render(request, 'web/erp/crear_material.html', {
        'form': form,
        'editando': True, 
        'material': material
    })
    
@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def realizar_ajuste(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        form = AjusteInventarioForm(request.POST)
        if form.is_valid():
            cantidad_ajuste = form.cleaned_data['cantidad_ajuste']
            observaciones = form.cleaned_data['observaciones']
            
            with transaction.atomic():
                material.stock_actual += cantidad_ajuste
                material.save()
                MovimientoInventario.objects.create(
                    material=material, tipo='AJUSTE', cantidad=cantidad_ajuste,
                    responsable=request.user, observaciones=observaciones
                )
            messages.success(request, f'¡Ajuste de {cantidad_ajuste} aplicado a {material.sku}!')
            return redirect('inventario_actual')
    else:
        form = AjusteInventarioForm()
        
    return render(request, 'web/erp/ajustar_inventario.html', {
        'form': form, 'material': material, 'rol': 'Administrador'
    })

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def eliminar_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    nombre_temp = material.nombre
    try:
        material.delete()
        messages.success(request, f'Material "{nombre_temp}" eliminado definitivamente.')
    except Exception: # Simplificado para evitar error de importación models.ProtectedError
        material.is_active = False
        material.save()
        messages.warning(request, f'El material "{nombre_temp}" tiene historial. Ha sido desactivado.')
    return redirect('inventario_actual')


# =======================================================
# MÓDULO DE PROYECTOS Y AUDITORÍA
# =======================================================

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def gestionar_proyectos(request):
    proyectos = Proyecto.objects.all().order_by('-fecha_creacion')
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Nuevo proyecto creado con éxito!")
            return redirect('gestionar_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'web/erp/gestionar_proyectos.html', {'proyectos': proyectos, 'form': form, 'rol': 'Administrador'})

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def alternar_estado_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    proyecto.is_active = not proyecto.is_active
    proyecto.save()
    estado = "activado" if proyecto.is_active else "desactivado"
    messages.success(request, f"Proyecto '{proyecto.nombre}' {estado} correctamente.")
    return redirect('gestionar_proyectos')

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def editar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Proyecto '{proyecto.nombre}' actualizado.")
    return redirect('gestionar_proyectos')

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def eliminar_proyecto_erp(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    nombre_temp = proyecto.nombre
    try:
        proyecto.delete()
        messages.success(request, f'Proyecto "{nombre_temp}" eliminado definitivamente.')
    except Exception:
        proyecto.is_active = False
        proyecto.save()
        messages.warning(request, f'El proyecto "{nombre_temp}" tiene requerimientos. Ha sido archivado.')
    return redirect('gestionar_proyectos')

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def historial_movimientos(request):
    movimientos_list = MovimientoInventario.objects.all().order_by('-fecha_hora')
    
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        movimientos_list = movimientos_list.filter(tipo=tipo_filtro)
        
    mes_filtro = request.GET.get('mes')
    if mes_filtro:
        try:
            year, month = mes_filtro.split('-')
            movimientos_list = movimientos_list.filter(fecha_hora__year=year, fecha_hora__month=month)
        except ValueError:
            pass 
            
    proyecto_id = request.GET.get('proyecto')
    if proyecto_id:
        movimientos_list = movimientos_list.filter(requerimiento_asociado__proyecto_id=proyecto_id)

    proyectos_activos = Proyecto.objects.filter(is_active=True).order_by('nombre')
    proyectos_inactivos = Proyecto.objects.filter(is_active=False).order_by('nombre')
            
    paginator = Paginator(movimientos_list, 30) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'web/erp/auditoria.html', {
        'page_obj': page_obj, 'tipo_filtro': tipo_filtro, 'mes_filtro': mes_filtro,
        'proyecto_id': proyecto_id, 'proyectos_activos': proyectos_activos,
        'proyectos_inactivos': proyectos_inactivos, 'rol': 'Administrador'
    })


# =======================================================
# MÓDULO DE REPORTES Y EXPORTACIÓN PDF
# =======================================================

@login_required(login_url='login')
def imprimir_pdf_ticket(request, req_id):
    ticket = get_object_or_404(Requerimiento, id=req_id)
    if not es_admin(request.user) and ticket.solicitante != request.user:
        messages.error(request, "No tienes permiso para ver este comprobante.")
        return redirect('dashboard_erp')
 
    context = {
        'ticket': ticket,
        'detalles': ticket.detalles.all(),
        'logo_path': os.path.join(settings.BASE_DIR, 'web', 'static', 'web', 'img', 'logo.jpg'),
        'fecha_impresion': timezone.now(),
    }
 
    html = get_template('web/erp/pdf_ticket.html').render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Comprobante_Entrega_{ticket.folio}.pdf"'
 
    if pisa.CreatePDF(html, dest=response).err:
        return HttpResponse('Hubo un error al generar el PDF del ticket.')
    return response

@login_required(login_url='login')
def imprimir_pdf_oc(request, oc_id):
    if not es_bodeguero(request.user) and not es_admin(request.user):
        messages.error(request, "No tienes permiso para imprimir órdenes de compra.")
        return redirect('dashboard_erp')
 
    oc = get_object_or_404(OrdenCompra, id=oc_id)
    context = {
        'oc': oc, 'detalles': oc.detalles.all(),
        'logo_path': os.path.join(settings.BASE_DIR, 'web', 'static', 'web', 'img', 'logo.jpg'),
        'fecha_impresion': timezone.now(),
    }
 
    html = get_template('web/erp/pdf_oc.html').render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="OrdenCompra_{oc.folio}.pdf"'
 
    if pisa.CreatePDF(html, dest=response).err:
        return HttpResponse('Hubo un error al generar el PDF de la orden de compra.')
    return response

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def imprimir_pdf_auditoria(request):
    movimientos = MovimientoInventario.objects.all().order_by('-fecha_hora')
    
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro: movimientos = movimientos.filter(tipo=tipo_filtro)
        
    mes_filtro = request.GET.get('mes')
    if mes_filtro:
        try:
            year, month = mes_filtro.split('-')
            movimientos = movimientos.filter(fecha_hora__year=year, fecha_hora__month=month)
        except ValueError: pass
            
    proyecto_obj = None
    proyecto_id = request.GET.get('proyecto')
    if proyecto_id:
        movimientos = movimientos.filter(requerimiento_asociado__proyecto_id=proyecto_id)
        proyecto_obj = get_object_or_404(Proyecto, id=proyecto_id)

    context = {
        'ingresos': movimientos.filter(tipo='INGRESO'),
        'salidas': movimientos.filter(tipo='SALIDA'),
        'ajustes': movimientos.filter(tipo='AJUSTE'),
        'tipo_filtro': tipo_filtro, 'mes_filtro': mes_filtro, 'proyecto': proyecto_obj,
        'logo_path': os.path.join(settings.BASE_DIR, 'web', 'static', 'web', 'img', 'logo.jpg'),
        'fecha_impresion': timezone.now(),
    }
    
    html = get_template('web/erp/pdf_auditoria.html').render(context)
    response = HttpResponse(content_type='application/pdf')
    nombre_archivo = f"Auditoria_{proyecto_obj.nombre.replace(' ', '_')}" if proyecto_obj else "Auditoria_Inventario_ProduMetal"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}.pdf"'
    
    if pisa.CreatePDF(html, dest=response).err:
        return HttpResponse('Hubo un error al generar el PDF de la auditoría.')
    return response


# =======================================================
# MÓDULO DE SEGURIDAD (Gestión de Bloqueos)
# =======================================================

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def gestionar_empleados(request):
    Group.objects.get_or_create(name='Bodeguero')
    Group.objects.get_or_create(name='Solicitante')
    Group.objects.get_or_create(name='Compras')
    
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

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def gestionar_bloqueos(request):
    intentos_fallidos = AccessAttempt.objects.all().order_by('-attempt_time')
    return render(request, 'web/erp/gestionar_bloqueos.html', {'intentos': intentos_fallidos})

@login_required(login_url='login')
@user_passes_test(es_admin, login_url='dashboard_erp')
def desbloquear_usuario(request, intento_id):
    intento = get_object_or_404(AccessAttempt, id=intento_id)
    usuario = intento.username
    intento.delete()
    messages.success(request, f"¡El usuario '{usuario}' ha sido desbloqueado con éxito! Ya puede iniciar sesión.")
    return redirect('gestionar_bloqueos')