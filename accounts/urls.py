from django.urls import path
from .views import user_login, user_register, user_logout, profile_view, user_logout, edit_profile

urlpatterns = [
    path("login/", user_login, name="login"),
    path("register/", user_register, name="register"),
    path("logout/", user_logout, name="logout"),
    path('profile/', profile_view, name='profile'),
    path('logout/', user_logout, name='logout'), 
    path('editar-perfil/', edit_profile, name='edit_profile'),
    ]