from django import forms
from .models import Requerimiento, DetalleRequerimiento, MovimientoInventario
from django.contrib.auth.models import User, Group
from .models import OrdenCompra, DetalleOrdenCompra, Material

class RequerimientoForm(forms.ModelForm):
    class Meta:
        model = Requerimiento
        fields = ['proyecto', 'observaciones']
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej. Materiales urgentes para montaje...'}),
        }

class DetalleRequerimientoForm(forms.ModelForm):
    class Meta:
        model = DetalleRequerimiento
        fields = ['material', 'cantidad_solicitada']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_solicitada': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.1', 'step': '0.01'}),
        }

class RegistroEmpleadoForm(forms.ModelForm):
    # Campo extra para elegir el rol
    rol = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Seleccione un cargo...",
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. jperez'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # Sobrescribimos el método save para encriptar la contraseña y asignar el rol
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Encriptación obligatoria
        if commit:
            user.save()
            rol = self.cleaned_data['rol']
            user.groups.add(rol) # Se le asigna el rol elegido en el formulario
        return user
    
class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['proveedor', 'numero_factura', 'observaciones', 'documento_respaldo']
        labels = {
            'proveedor': 'Nombre del Proveedor / Empresa',
            'numero_factura': 'N° de Factura (Opcional)',
            'observaciones': 'Notas o Comentarios',
            'documento_respaldo': 'Subir Factura PDF (Opcional)',
        }
        widgets = {
            'proveedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Aceros del Ecuador S.A.'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 001-002-000012345'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documento_respaldo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class DetalleOrdenCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleOrdenCompra
        fields = ['material', 'cantidad_pedida']
        labels = {
            'material': 'Seleccionar Material/Insumo',
            'cantidad_pedida': 'Cantidad',
        }
        widgets = {
            'material': forms.Select(attrs={'class': 'form-select fw-bold'}),
            'cantidad_pedida': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

from django import forms
from .models import Proyecto

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'centro_costos', 'is_active']
        labels = {
            'nombre': 'Nombre del Proyecto',
            'centro_costos': 'Centro de Costos (ID Único)',
            'is_active': '¿Proyecto Activo?',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Ej: Estructura Galpón Sector A'
            }),
            'centro_costos': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Ej: PM-2024-001'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['sku', 'nombre', 'tipo', 'descripcion', 'stock_actual', 'stock_minimo', 'ubicacion']
        labels = {
            'sku': 'Código / SKU',
            'nombre': 'Nombre del Material',
            'tipo': 'Categoría',
            'descripcion': 'Descripción (opcional)',
            'stock_actual': 'Cantidad inicial en bodega',
            'stock_minimo': 'Stock mínimo (alerta)',
            'ubicacion': 'Ubicación en bodega',
        }
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ACE-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tubo cuadrado 40x40'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pasillo A, Estante 3'}),
        }