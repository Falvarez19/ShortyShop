# ShortyShop/settings.py
from pathlib import Path
import os
import dj_database_url   # ← FALTABA ESTE IMPORT

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / entorno ---
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,.fly.dev"
).split(",")

CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", "https://*.fly.dev"
).split(",")

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",     # WhiteNoise usa esta
    "shop",
    "accounts",
]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← Añadido (sirve /static)
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ShortyShop.urls"
WSGI_APPLICATION = "ShortyShop.wsgi.application"

# --- Base de datos: usa /data/db.sqlite3 si no hay DATABASE_URL ---
DEFAULT_DB_URL = os.getenv("DATABASE_URL", "sqlite:////data/db.sqlite3")
DATABASES = {
    "default": dj_database_url.config(
        default=DEFAULT_DB_URL, conn_max_age=600, ssl_require=False
    )
}

# --- i18n ---
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# --- Static (WhiteNoise) ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Media (volumen en Fly: /data/media) ---
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "/data/media" if not DEBUG else BASE_DIR / "media"))

# --- Dev helper (mimes) ---
if DEBUG:
    import mimetypes
    mimetypes.add_type("text/css", ".css", True)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Auth custom ---
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_USER_MODEL = "accounts.CustomUser"

# --- SSL detrás de proxy ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
