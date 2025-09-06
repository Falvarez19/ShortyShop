# Railway deploy - ShortyShop

1) Variables en servicio web:
   - DJANGO_SECRET_KEY (clave larga)
   - DJANGO_DEBUG=0
   - ALLOWED_HOSTS=tuapp.up.railway.app,localhost,127.0.0.1
   - CSRF_TRUSTED_ORIGINS=web-production-60f6.up.railway.app
   - PYTHONUNBUFFERED=1
   - PYTHONDONTWRITEBYTECODE=1

2) Base de datos:
   - Plugin PostgreSQL → Connect/Link al servicio web
   - DATABASE_URL = ${{ Postgres.DATABASE_URL }}
   - (si usás URL pública) DATABASE_SSL_REQUIRE=1

3) Procfile:
   web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ShortyShop.wsgi:application --bind 0.0.0.0:$PORT

4) CustomUser: detectado y AUTH_USER_MODEL configurado.
