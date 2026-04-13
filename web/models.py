from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import datetime

# 1. Modelo de Proyectos (Con Soft Delete)
class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)
    centro_costos = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True, help_text="Desmarcar para borrado lógico")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.centro_costos} - {self.nombre}"

# 2. Catálogo de Materiales (Con alertas de stock y Soft Delete)
class Material(models.Model):
    sku = models.CharField(max_length=50, unique=True, verbose_name="Código/SKU")
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=5.00, help_text="Umbral para alertas")
    ubicacion = models.CharField(max_length=100, help_text="Ej. Pasillo A, Estante 3")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Materiales"

    def __str__(self):
        return f"{self.sku} - {self.nombre} (Stock: {self.stock_actual})"

# 3. Requerimientos / Tickets
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
        # Autogenerador de Folio (Ej. REQ-2026-001)
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

# 4. Detalle de Requerimiento (Qué y Cuánto)
class DetalleRequerimiento(models.Model):
    requerimiento = models.ForeignKey(Requerimiento, related_name='detalles', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    cantidad_solicitada = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_despachada = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.cantidad_solicitada} de {self.material.nombre} para {self.requerimiento.folio}"

# 5. Historial de Movimientos (Trazabilidad y Certificados de Calidad)
class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('INGRESO', 'Ingreso por Compra'),
        ('SALIDA', 'Salida por Requerimiento'),
        ('AJUSTE', 'Ajuste de Inventario'),
    ]

    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=15, choices=TIPO_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora = models.DateTimeField(default=timezone.now)
    responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    requerimiento_asociado = models.ForeignKey(Requerimiento, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Archivo PDF obligatorio solo en formato .pdf
    certificado_calidad = models.FileField(
        upload_to='certificados/%Y/%m/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Subir solo archivos PDF"
    )

    class Meta:
        verbose_name_plural = "Movimientos de Inventario"

    def __str__(self):
        return f"{self.tipo} - {self.cantidad} de {self.material.nombre} ({self.fecha_hora.strftime('%Y-%m-%d')})"