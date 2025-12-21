#!/bin/bash

# Script para deploy y actualizaciones en Render.com
# Uso: ./deploy-render.sh [comando]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDER_URL="${RENDER_URL:-https://portfolio-render.onrender.com}"
RENDER_SERVICE_ID="${RENDER_SERVICE_ID:-}"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar requirements
check_requirements() {
    log_info "Verificando requisitos..."
    
    if ! command -v git &> /dev/null; then
        log_error "Git no está instalado"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 no está instalado"
        exit 1
    fi
    
    log_success "Todos los requisitos verificados"
}

# Exportar datos locales
export_data() {
    log_info "Exportando datos desde SQLite local..."
    
    cd "$PROJECT_DIR"
    python3 -m venv venv 2>/dev/null || true
    source venv/bin/activate
    
    cd app
    python manage.py dumpdata --natural-foreign > ../datos_full.json
    
    log_success "Datos exportados a datos_full.json"
    
    # Crear versión comprimida
    gzip -c ../datos_full.json > ../datos_full.json.gz
    
    echo ""
    echo "📊 Estadísticas:"
    ls -lh ../datos_full.json
    ls -lh ../datos_full.json.gz
}

# Preparar para deploy
prepare_deploy() {
    log_info "Preparando para deploy..."
    
    cd "$PROJECT_DIR"
    
    # Verificar que todo esté en git
    if [[ -n $(git status -s) ]]; then
        log_warning "Hay cambios sin commitear"
        git status
        
        read -p "¿Deseas continuador? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Deploy cancelado"
            exit 1
        fi
    fi
    
    log_success "Todo preparado para deploy"
}

# Deploy a Render
deploy() {
    log_info "Iniciando deploy a Render.com..."
    
    cd "$PROJECT_DIR"
    
    # Preparar
    prepare_deploy
    
    # Push a main (Render monitorea main/master por defecto)
    log_info "Pushing a repositorio remoto..."
    git push origin main
    
    log_success "Push completado!"
    echo ""
    echo "🌐 URL de la aplicación: $RENDER_URL"
    echo ""
    echo "📋 Próximos pasos:"
    echo "  1. Abre tu dashboard de Render"
    echo "  2. Selecciona tu servicio 'portfolio'"
    echo "  3. El deploy debería iniciarse automáticamente"
    echo "  4. Monitorea los logs en Render durante el deploy"
}

# Migrar datos a Render
migrate_data() {
    log_info "Preparando migración de datos..."
    
    cd "$PROJECT_DIR"
    
    # Exportar datos si no existen
    if [[ ! -f "datos_full.json" ]]; then
        log_warning "No existe datos_full.json, exportando..."
        export_data
    fi
    
    log_info "Carga de datos en Render manual:"
    echo ""
    echo "Opción 1: Via PSQL (en tu máquina local)"
    echo "  psql \$DATABASE_URL < datos_backup.sql"
    echo ""
    echo "Opción 2: Via Django Management Command (en Render)"
    echo "  1. Conéctate a Render Shell:"
    echo "     render shell"
    echo ""
    echo "  2. Carga los datos (si están en el repo):"
    echo "     python manage.py loaddata datos_full.json"
    echo ""
    echo "Opción 3: Via API de Render (recomendado)"
    echo "  1. Ve a tu dashboard de Render"
    echo "  2. En tu servicio, ve a 'Shell'"
    echo "  3. Sube el archivo datos_full.json"
    echo "  4. Ejecuta: python manage.py loaddata datos_full.json"
}

# Crear backup de la BD
backup_database() {
    log_info "Creando backup de la BD..."
    
    if [[ -z $DATABASE_URL ]]; then
        log_error "DATABASE_URL no está configurada"
        exit 1
    fi
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="backup_${TIMESTAMP}.sql"
    
    pg_dump "$DATABASE_URL" > "$BACKUP_FILE"
    
    log_success "Backup creado: $BACKUP_FILE"
    ls -lh "$BACKUP_FILE"
}

# Mostrar logs
show_logs() {
    log_info "Para ver los logs en Render:"
    echo ""
    echo "1. Ve a https://dashboard.render.com"
    echo "2. Selecciona tu servicio 'portfolio'"
    echo "3. Ve a la pestaña 'Logs'"
    echo "4. O usa la consola de Render para comandos específicos"
}

# Help
show_help() {
    cat << EOF
$BLUE🚀 Deploy y Update Script para Render.com$NC

Uso: ./deploy-render.sh [comando]

Comandos disponibles:

  export        Exportar datos desde SQLite local
  deploy        Deploy a Render.com
  migrate       Preparar migración de datos
  backup        Crear backup de la BD de Render
  logs          Ver información sobre logs
  help          Mostrar esta ayuda

Ejemplos:

  # Exportar datos locales
  ./deploy-render.sh export

  # Deploy completo
  ./deploy-render.sh deploy

  # Migrar datos después del deploy
  ./deploy-render.sh migrate

Configuración recomendada:

  En Render Dashboard:
  1. Crea un Web Service
  2. Conecta tu repositorio GitHub
  3. En "Publish route", usa: /
  4. Build Command: pip install -r requirements.txt && cd app && python manage.py collectstatic --noinput
  5. Start Command: gunicorn app.wsgi:application --bind 0.0.0.0:\$PORT
  6. Agrega variables de entorno:
     - SECRET_KEY (tu Django secret)
     - DEBUG=false
     - ALLOWED_HOSTS=tu-dominio.onrender.com
  7. En Runtime, selecciona Python 3.12
  8. Haz clic en "Create Web Service"

EOF
}

# Main
main() {
    local cmd="${1:-help}"
    
    case $cmd in
        export)
            check_requirements
            export_data
            ;;
        deploy)
            check_requirements
            deploy
            ;;
        migrate)
            migrate_data
            ;;
        backup)
            backup_database
            ;;
        logs)
            show_logs
            ;;
        help)
            show_help
            ;;
        *)
            log_error "Comando desconocido: $cmd"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
