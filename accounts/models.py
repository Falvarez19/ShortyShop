# ============================================
# =============== #ACCOUNT MODELS ============
# Usuario custom con email como identificador
# ============================================

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# --------------------------------------------
# Manager del usuario: crea users y superusers
# --------------------------------------------
class CustomUserManager(BaseUserManager):
    # Crea un usuario normal usando email como username
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Crea un superusuario con permisos de staff y superuser
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# --------------------------------------------
# Modelo de usuario: email único como username
# --------------------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # Flags requeridos por Django Admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Manager
    objects = CustomUserManager()

    # Autenticación por email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ("email",)

    # Devuelve el identificador textual del usuario
    def __str__(self):
        return self.email

    # Retorna el nombre completo (helper útil en admin/plantillas)
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    # Retorna el nombre corto (helper estándar de Django)
    def get_short_name(self) -> str:
        return self.first_name or self.email.split("@")[0]
