# ===============================
# ============ IMPORTS ==========
# ===============================
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .forms import CustomUserCreationForm, UpdateAddressForm


# ==========================================================
# =======================  #AUTH  ==========================
# ============ (Login, Registro, Logout) ===================
# ==========================================================

# Muestra el formulario de login y autentica por email/username
def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        # AuthenticationForm espera "username"; usamos email como username
        email = request.POST.get("username") or request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get("next") or "home"
            return redirect(next_url)
        else:
            messages.error(request, "Correo o contraseña incorrectos.")

    return render(request, "accounts/login.html", {
        "form": form,
        "next": request.GET.get("next", ""),
    })


# Registra un nuevo usuario y lo inicia sesión
def user_register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Especifica backend de autenticación para login directo
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)

            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


# Cierra la sesión del usuario actual
def user_logout(request):
    logout(request)
    return redirect("home")


# ==========================================================
# =====================  #PERFIL  ==========================
# =============== (Ver y editar perfil) ====================
# ==========================================================

# Muestra el perfil del usuario logueado
@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


# Edita dirección y contraseña del perfil
@login_required
def edit_profile(request):
    address_form = UpdateAddressForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        address_form = UpdateAddressForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        if address_form.is_valid():
            address_form.save()
            messages.success(request, "Dirección actualizada correctamente.")

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # evita logout tras cambiar clave
            messages.success(request, "Contraseña actualizada correctamente.")

        return redirect("profile")

    return render(request, "accounts/edit_profile.html", {
        "address_form": address_form,
        "password_form": password_form,
    })
