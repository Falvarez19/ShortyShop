FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/venv/bin:$PATH" \
    PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /venv && pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

RUN mkdir -p /data/media && chmod -R 777 /data

EXPOSE 8080
CMD ["sh","-c","mkdir -p /data/media && chmod 777 /data/media && \
python manage.py migrate --noinput && \
exec gunicorn ShortyShop.wsgi:application -b 0.0.0.0:8080 --workers 2 --timeout 120 --access-logfile - --error-logfile - --log-level debug"]