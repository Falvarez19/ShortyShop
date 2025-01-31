from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Vista para el login
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)  # Se usa "username=email"
        
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next") or "home"
            return redirect(next_url)
        else:
            messages.error(request, "Correo o contraseña incorrectos.")

    return render(request, "accounts/login.html", {"next": request.GET.get("next", "")})
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
    logout(request)
    return redirect('home')  # Asegúrate de que 'home' es el nombre de la vista de inicio

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')