# Usar imagen Python oficial
FROM python:3.12-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copiar proyecto
COPY . .

# Crear directorio para datos estáticos
RUN mkdir -p /app/staticfiles /app/photos

# Recolectar archivos estáticos
RUN cd /app && python manage.py collectstatic --noinput --clear

# Comando para correr la aplicación
CMD ["sh", "-c", "cd /app && python manage.py migrate && gunicorn app.app.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120"]
