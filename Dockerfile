FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# deps de sistema (psycopg/pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# primero deps (mejor cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# proyecto
COPY . .

# carpeta para sqlite (si querés persistir con volumen)
RUN mkdir -p /app/data

# envs útiles
ENV DJANGO_SETTINGS_MODULE=ShortyShop.settings \
    PYTHONPATH=/app

# usuario no root
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

CMD ["./entrypoint.sh"]
