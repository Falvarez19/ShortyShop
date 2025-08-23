#!/usr/bin/env bash
set -e

# Variables por si querés sobreescribir la ruta del sqlite en fly.toml
export SQLITE_PATH=${SQLITE_PATH:-/app/data/db.sqlite3}

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Ajusta "shortyshop.wsgi" al paquete de tu proyecto
exec gunicorn shortyshop.wsgi:application \
  --bind 0.0.0.0:${PORT} \
  --workers 3 \
  --timeout 60
