# Usar Python 3.12 slim
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Paquetes del sistema (psycopg2/whitenoise no necesitan mucho)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Carpeta de la app
WORKDIR /app

# Requisitos
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar proyecto
COPY . /app

# Static (si falla en build no es crítico; también lo corremos en entrypoint)
RUN python manage.py collectstatic --noinput || true

# Puerto
EXPOSE 8080

# Entrypoint (migra DB, collectstatic y levanta gunicorn)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
