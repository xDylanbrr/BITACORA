from django import forms
from .models import Usuario, Registro


class LoginForm(forms.Form):
    codigo_empleado = forms.CharField(
        label='Código de empleado',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'auth-input',
            'placeholder': '0001',
            'inputmode': 'numeric',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña inicial',
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': 'Contraseña que usará para iniciar sesión',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'rol', 'codigo_empleado', 'departamento', 'telefono', 'cedula', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nombre y apellido'}),
            'rol': forms.Select(attrs={'class': 'auth-input auth-select'}),
            'codigo_empleado': forms.TextInput(attrs={'class': 'auth-input', 'placeholder': '0002', 'inputmode': 'numeric', 'maxlength': '10'}),
            'departamento': forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Control de Calidad'}),
            'telefono': forms.TextInput(attrs={'class': 'auth-input', 'placeholder': '809-000-0000', 'inputmode': 'numeric', 'maxlength': '12'}),
            'cedula': forms.TextInput(attrs={'class': 'auth-input', 'placeholder': '000-0000000-0', 'inputmode': 'numeric', 'maxlength': '13'}),
            'email': forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'usuario@gtg.com'}),
        }
        labels = {
            'nombre': 'Nombre completo',
            'rol': 'Rol',
            'codigo_empleado': 'Código de empleado',
            'departamento': 'Departamento',
            'telefono': 'Teléfono',
            'cedula': 'Cédula de identidad',
            'email': 'Correo electrónico',
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario


# Campos comunes de cabecera de registro (compartidos por los 3 formularios)
class RegistroCabeceraForm(forms.Form):
    turno = forms.ChoiceField(
        choices=Registro.TURNO_CHOICES,
        widget=forms.HiddenInput()
    )
    fecha = forms.DateField(
        widget=forms.HiddenInput()
    )
    hora_inicio = forms.TimeField(
        widget=forms.HiddenInput()
    )
    maquina = forms.CharField(max_length=100)
    mo = forms.CharField(max_length=50, label='MO #')
    item = forms.CharField(max_length=20, label='Ítem', required=False)
    descripcion = forms.CharField(max_length=200, label='Descripción del producto')
    auditor = forms.CharField(max_length=100, required=False)
    supervisor = forms.CharField(max_length=100, required=False)
