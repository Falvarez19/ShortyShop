"""
Django settings for ShortyShop project (Fly.io + Docker).
"""

from pathlib import Path
import os

# -------------------
# Paths
# -------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------
# App name (opcional, útil para construir URLs/hosts dinámicos)
# -------------------
APP_NAME = "shortyshop"  # <- tu app en Fly

# -------------------
# Seguridad / Entorno
# -------------------
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "CHANGE_ME_IN_PRODUCTION_super_inseguro"
)

DEBUG = os.getenv("DEBUG", "0") not in ["0", "false", "False", "FALSE"]

# Hosts y CSRF
DEFAULT_ALLOWED = f"{APP_NAME}.fly.dev,localhost,127.0.0.1"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", DEFAULT_ALLOWED).split(",") if h.strip()]

DEFAULT_TRUSTED = f"https://{APP_NAME}.fly.dev"
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", DEFAULT_TRUSTED).split(",") if o.strip()]

# -------------------
# Aplicaciones
# -------------------
INSTALLED_APPS = [
    # WhiteNoise desactiva el static server de runserver (opcional)
    "whitenoise.runserver_nostatic",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "shop",
    "accounts",
]

# -------------------
# Middleware
# -------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise para servir estáticos
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ShortyShop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # podés agregar carpetas de templates personalizadas acá
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ShortyShop.wsgi.application"

# -------------------
# Base de datos (SQLite en volumen)
# -------------------
SQLITE_PATH = os.getenv("SQLITE_PATH", str(BASE_DIR / "db.sqlite3"))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": SQLITE_PATH,
    }
}

# -------------------
# Password validators
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------
# Internacionalización
# -------------------
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# Separadores de miles/decimales
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = "."
DECIMAL_SEPARATOR = ","
NUMBER_GROUPING = 3

# -------------------
# Archivos estáticos y media
# -------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # para tus assets en el repo
STATIC_ROOT = BASE_DIR / "staticfiles"    # donde collectstatic deposita

# WhiteNoise storage con compresión + manifest
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 30  # 30 días

# Media (persistida en volumen)
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "/app/data/media"))

# -------------------
# Auth custom
# -------------------
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_USER_MODEL = "accounts.CustomUser"

# -------------------
# Seguridad detrás de proxy (Fly)
# -------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# -------------------
# Mimetypes (útil en dev)
# -------------------
if DEBUG:
    import mimetypes
    mimetypes.add_type("text/css", ".css", True)

# -------------------
# Default PK
# -------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
