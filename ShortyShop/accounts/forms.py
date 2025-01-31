from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Introduce una dirección de correo válida.")
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    address = forms.CharField(max_length=255, required=True, label="Dirección", widget=forms.TextInput(attrs={"placeholder": "Ejemplo: Calle Falsa 123"}))
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),  # Permite que se seleccione desde un calendario
        label="Fecha de nacimiento"
    )

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "address", "birth_date", "password1", "password2"]

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Introduce tu correo"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Introduce tu contraseña"}),
    )