# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/venv/bin:$PATH" \
    PORT=8080

WORKDIR /app

# deps del sistema para psycopg2 y compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# venv + python deps
COPY requirements.txt .
RUN python -m venv /venv && pip install --upgrade pip && pip install -r requirements.txt

# copia del código
COPY . .

# colecta estáticos (WhiteNoise)
RUN python manage.py collectstatic --noinput

# crea carpeta para media (la montaremos como volumen)
RUN mkdir -p /data/media && chmod -R 777 /data

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "ShortyShop.wsgi:application", "--workers", "3", "--timeout", "120"]
