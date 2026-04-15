from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import datetime

# 1. Modelo de Proyectos
class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)
    centro_costos = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True, help_text="Desmarcar para borrado lógico")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.centro_costos} - {self.nombre}"

# 2. Catálogo de Inventario (¡NUEVO: Separación Material vs Consumible!)
class Material(models.Model):
    TIPO_CATEGORIA = [
        ('MATERIAL', 'Material Estructural / Acero'),
        ('CONSUMIBLE', 'Consumible / Herramienta Menor'),
    ]

    sku = models.CharField(max_length=50, unique=True, verbose_name="Código/SKU")
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CATEGORIA, default='MATERIAL') # <-- NUEVO FILTRO
    descripcion = models.TextField(blank=True, null=True)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=5.00, help_text="Umbral para alertas")
    ubicacion = models.CharField(max_length=100, help_text="Ej. Pasillo A, Estante 3")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Inventario (Materiales y Consumibles)"

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.sku} - {self.nombre} (Stock: {self.stock_actual})"

# =====================================================================
# NUEVO MÓDULO: ABASTECIMIENTO Y COMPRAS
# =====================================================================
class OrdenCompra(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador (Cotizando)'),
        ('EMITIDA', 'Emitida al Proveedor'),
        ('RECIBIDA', 'Recibida en Bodega (Stock Actualizado)'),
        ('CANCELADA', 'Cancelada'),
    ]

    folio = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    proveedor = models.CharField(max_length=200, help_text="Nombre de la ferretería o distribuidor")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ordenes_compra')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')
    
    # Aquí se guardará la factura o guía de remisión del proveedor
    documento_respaldo = models.FileField(
        upload_to='compras_facturas/%Y/%m/', 
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png'])],
        help_text="Sube la factura, nota de venta o guía de remisión"
    )

    def save(self, *args, **kwargs):
        # Autogenerador de Folio de Compra (Ej. OC-2026-001)
        if not self.folio:
            year = datetime.date.today().year
            ultima_oc = OrdenCompra.objects.filter(folio__startswith=f'OC-{year}').order_by('id').last()
            if ultima_oc:
                secuencia = int(ultima_oc.folio.split('-')[-1]) + 1
            else:
                secuencia = 1
            self.folio = f'OC-{year}-{secuencia:03d}'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Órdenes de Compra"

    def __str__(self):
        return f"{self.folio} - {self.proveedor} ({self.estado})"

class DetalleOrdenCompra(models.Model):
    orden = models.ForeignKey(OrdenCompra, related_name='detalles', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    cantidad_pedida = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Opcional a futuro

    def __str__(self):
        return f"{self.cantidad_pedida} de {self.material.nombre} (OC: {self.orden.folio})"


# =====================================================================
# MÓDULO DE REQUERIMIENTOS INTERNOS (Técnicos pidiendo a Bodega)
# =====================================================================
class Requerimiento(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('DESPACHADO', 'Despachado'),
    ]

    folio = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT, related_name='requerimientos')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.PROTECT)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    observaciones = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Autogenerador de Folio de Requerimiento (Ej. REQ-2026-001)
        if not self.folio:
            year = datetime.date.today().year
            ultimo_req = Requerimiento.objects.filter(folio__startswith=f'REQ-{year}').order_by('id').last()
            if ultimo_req:
                secuencia = int(ultimo_req.folio.split('-')[-1]) + 1
            else:
                secuencia = 1
            self.folio = f'REQ-{year}-{secuencia:03d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio} - {self.proyecto.nombre} ({self.estado})"

class DetalleRequerimiento(models.Model):
    requerimiento = models.ForeignKey(Requerimiento, related_name='detalles', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    cantidad_solicitada = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_despachada = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.cantidad_solicitada} de {self.material.nombre} para {self.requerimiento.folio}"

# =====================================================================
# AUDITORÍA Y TRAZABILIDAD (Historial Inalterable)
# =====================================================================
class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('INGRESO', 'Ingreso por Compra (Abastecimiento)'),
        ('SALIDA', 'Salida por Requerimiento (Despacho)'),
        ('AJUSTE', 'Ajuste Manual de Inventario'),
    ]

    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=15, choices=TIPO_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora = models.DateTimeField(default=timezone.now)
    responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    
    # Enlaces cruzados para saber exactamente DE DÓNDE vino o A DÓNDE fue
    requerimiento_asociado = models.ForeignKey(Requerimiento, on_delete=models.SET_NULL, null=True, blank=True)
    orden_compra_asociada = models.ForeignKey(OrdenCompra, on_delete=models.SET_NULL, null=True, blank=True)
    
    certificado_calidad = models.FileField(
        upload_to='certificados/%Y/%m/', blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Opcional: Certificado de calidad del lote de acero"
    )

    class Meta:
        verbose_name_plural = "Bitácora de Movimientos (Auditoría)"

    def __str__(self):
        return f"{self.tipo} - {self.cantidad} de {self.material.nombre} ({self.fecha_hora.strftime('%d/%m/%Y')})"