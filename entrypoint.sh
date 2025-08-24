#!/usr/bin/env bash
set -e

# Migraciones y static
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

# Gunicorn (WSGI)
exec gunicorn ShortyShop.wsgi:application \
  --bind 0.0.0.0:8080 \
  --workers 3 \
  --timeout 60
