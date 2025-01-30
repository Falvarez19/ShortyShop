from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm
from .forms import CustomAuthenticationForm

# Vista para el login
def user_login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # Redirige a la página principal después de iniciar sesión
    else:
        form = CustomAuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})
# Vista para el registro
def user_register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente después de registrarse
            return redirect("home")  # Redirige a la página principal
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})

# Vista para el logout
def user_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")  # Redirige al home después de cerrar sesión
