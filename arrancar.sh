#!/bin/bash

# --- Colores ---
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

printf "${BLUE}===> Iniciando Reparación y Arranque <===${NC}\n"

# 1. Limpieza de temporales (Evita conflictos de importación)
printf "🧹 Limpiando archivos temporales y cache...\n"
find . -path "*/__pycache__" -delete
find . -name "*.pyc" -delete
find . -name ".DS_Store" -delete

# 2. Gestión del Entorno Virtual
if [ ! -d "venv" ]; then
    printf "📦 Creando venv nuevo...\n"
    python3 -m venv venv
fi

source venv/bin/activate

# Cargar variables de entorno desde .env si existe
if [ -f .env ]; then
    printf "🔐 Cargando variables de entorno desde .env...\n"
    export $(grep -v '^#' .env | xargs)
fi

# 3. Instalación de dependencias
printf "🔄 Actualizando pip e instalando dependencias...\n"
pip install --upgrade pip > /dev/null
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 6. Ejecución
printf "⚙️  Migrando base de datos...\n"
python manage.py makemigrations
python manage.py migrate

if [ $? -eq 0 ]; then
    # 7. Tests (Opcional)
    printf "${BLUE}¿Quieres lanzar los tests? (y/n): ${NC}"
    read -r response
    case "$response" in
        [yY]|[yY][eE][sS])
            printf "🧪 Ejecutando tests...\n"
            export DJANGO_ENV=testing
            python manage.py test
            test_exit_code=$?
            unset DJANGO_ENV
            
            if [ $test_exit_code -ne 0 ]; then
                printf "${RED}❌ Los tests han fallado. Abortando.${NC}\n"
                exit 1
            fi
            
            printf "${BLUE}✅ Tests pasados. ¿Quieres arrancar el servidor ahora? (y/n): ${NC}"
            read -r run_server
            case "$run_server" in
                [yY]|[yY][eE][sS])
                    printf "${GREEN}🚀 Arrancando servidor...${NC}\n"
                    python manage.py runserver
                    ;;
                *)
                    printf "${BLUE}👋 Tests finalizados con éxito. Saliendo sin arrancar el servidor.${NC}\n"
                    exit 0
                    ;;
            esac
            ;;
        *)
            printf "${GREEN}🚀 Arrancando servidor...${NC}\n"
            python manage.py runserver
            ;;
    esac
fi