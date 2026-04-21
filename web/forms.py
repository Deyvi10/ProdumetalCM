from django import forms
from .models import Requerimiento, DetalleRequerimiento, MovimientoInventario
from django.contrib.auth.models import User, Group
from .models import OrdenCompra, DetalleOrdenCompra

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
        fields = ['proveedor', 'documento_respaldo']
        widgets = {
            'proveedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Proveedor / Ferretería'}),
            'documento_respaldo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DetalleOrdenCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleOrdenCompra
        fields = ['material', 'cantidad_pedida']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_pedida': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.1'}),
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