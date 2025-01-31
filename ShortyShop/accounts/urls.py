from django.urls import path
from .views import user_login, user_register, user_logout, profile_view, user_logout
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", user_login, name="login"),
    path("register/", user_register, name="register"),
    path("logout/", user_logout, name="logout"),
    path("password_change/", auth_views.PasswordChangeView.as_view(template_name="accounts/password_change.html"), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"), name="password_change_done"),
    path('profile/', profile_view, name='profile'),
    path('logout/', user_logout, name='logout'), 
    ]