# Usar una imagen oficial de Python ligera
FROM python:3.13-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Evitar que Python escriba archivos .pyc y forzar salida sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend
COPY . .

# Exponer el puerto que Railway usará
EXPOSE $PORT

# Comando para ejecutar la aplicación con Gunicorn
# Nota: 'config.wsgi' es la ruta a tu archivo WSGI dentro de la carpeta 'config'
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"]