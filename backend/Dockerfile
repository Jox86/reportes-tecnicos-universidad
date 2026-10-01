# Dockerfile para el backend - Sistema de Reportes Técnicos
# Actualizado: 01/10/2026 - Forzar rebuild con cache bust v6

FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cache-bust: 2026-10-01-0006  ← Cambiar número si es necesario
RUN echo "BUILD_ID=2026-10-01-0010"
COPY . .

EXPOSE $PORT

CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"]