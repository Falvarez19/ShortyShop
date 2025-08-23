# Imagen base (Python 3.11 para evitar líos)
FROM python:3.11-slim

# Variables para que Python no genere .pyc y no use buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Dependencies primero (mejor cache)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el proyecto
COPY . /app

# WhiteNoise: crear dir de estáticos (colectaremos en runtime)
RUN mkdir -p /app/staticfiles

# Puerto para Fly (usaremos 8080)
ENV PORT=8080
EXPOSE 8080

# Entrypoint (migraciones + collectstatic + gunicorn)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
