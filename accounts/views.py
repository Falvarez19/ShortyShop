from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, UpdateAddressForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        email = request.POST.get("username") or request.POST.get("email") # AuthenticationForm espera un campo "username"
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
        "next": request.GET.get("next", "")
    })
# Vista para el registro
def user_register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Especificamos el backend de autenticación manualmente
            user.backend = "django.contrib.auth.backends.ModelBackend"

            login(request, user)  # Iniciar sesión automáticamente después de registrarse
            return redirect("home")  # Redirige a la página de inicio

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
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada correctamente.")

        return redirect("profile")

    return render(request, "accounts/edit_profile.html", {
        "address_form": address_form,
        "password_form": password_form
    })