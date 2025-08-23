from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "birth_date", "is_staff", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("address", "birth_date")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("email", "first_name", "last_name", "birth_date", "password1", "password2")}),
    )

    ordering = ['email']  # 👈 Cambiar 'username' por 'email'


admin.site.register(CustomUser, CustomUserAdmin)
