from django.contrib import admin
from .models import Proyecto, Material, Requerimiento, DetalleRequerimiento, MovimientoInventario

# Registro básico para el panel de control de Django
admin.site.register(Proyecto)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'stock_actual', 'stock_minimo', 'ubicacion', 'is_active')
    list_filter = ('is_active', 'ubicacion')
    search_fields = ('sku', 'nombre')

class DetalleRequerimientoInline(admin.TabularInline):
    model = DetalleRequerimiento
    extra = 1

@admin.register(Requerimiento)
class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ('folio', 'solicitante', 'proyecto', 'fecha_solicitud', 'estado')
    list_filter = ('estado', 'proyecto', 'fecha_solicitud')
    search_fields = ('folio', 'solicitante__username')
    inlines = [DetalleRequerimientoInline]
    readonly_fields = ('folio',)

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('material', 'tipo', 'cantidad', 'fecha_hora', 'responsable')
    list_filter = ('tipo', 'fecha_hora')
    search_fields = ('material__nombre', 'responsable__username')