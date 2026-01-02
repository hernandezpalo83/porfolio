#!/bin/bash

# --- Colores ---
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===> Iniciando Reparación y Arranque <===${NC}"

# 1. Limpieza de temporales (Evita conflictos de importación)
echo -e "🧹 Limpiando archivos temporales y cache..."
find . -path "*/__pycache__" -delete
find . -name "*.pyc" -delete

# 2. Gestión del Entorno Virtual
if [ ! -d "venv" ]; then
    echo -e "📦 Creando venv nuevo..."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. Forzar reinstalación de la librería conflictiva
echo -e "🔄 Asegurando librería captcha..."
pip install --upgrade pip > /dev/null
pip install --force-reinstall django-recaptcha

# 4. Instalación del resto
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 6. Ejecución
echo -e "⚙️  Migrando base de datos..."
python manage.py makemigrations
python manage.py migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}🚀 Arrancando servidor...${NC}"
    python manage.py runserver
fi