#!/bin/bash

# Deploy script para porfolio en Fly.io
# Uso: ./deploy.sh [mensaje]
# Ejemplo: ./deploy.sh "Fix: Actualizar galería de imágenes"

set -e

# Variables
APP_NAME="porfolio-polished-water-5224"
REGION="ams"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
log() {
  echo -e "${GREEN}[DEPLOY]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1" >&2
  exit 1
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

# Verificar que flyctl está instalado
if ! command -v flyctl &> /dev/null; then
  error "flyctl no está instalado. Instálalo con: curl -L https://fly.io/install.sh | sh"
fi

# Verificar que estamos en el directorio correcto
if [[ ! -f "fly.toml" || ! -f "Dockerfile" ]]; then
  error "No se encontró fly.toml o Dockerfile. Asegúrate de estar en el directorio raíz del proyecto."
fi

# Mensaje de confirmación (opcional)
COMMIT_MSG="${1:-Deployment desde script}"

log "Iniciando despliegue de ${APP_NAME}..."
log "Mensaje: ${COMMIT_MSG}"
echo ""

# Paso 1: Verificar que el repositorio git está limpio (opcional)
if [[ -d ".git" ]]; then
  if [[ -n $(git status -s) ]]; then
    warn "Hay cambios sin confirmar en git"
    log "Cambios:"
    git status -s
    echo ""
    read -p "¿Deseas continuar? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      error "Despliegue cancelado"
    fi
  fi
fi

# Paso 2: Compilar y desplegar remotamente
log "Compilando imagen Docker y desplegando en Fly..."
flyctl deploy --app $APP_NAME --remote-only

if [[ $? -eq 0 ]]; then
  log "¡Despliegue exitoso!"
  log "Tu app está disponible en:"
  log "  - https://${APP_NAME}.fly.dev"
  log "  - https://porfolio.hernandezpalo.es (después de configurar DNS)"
  echo ""
  log "Estado de máquinas:"
  flyctl machines list --app $APP_NAME
  echo ""
  log "Para ver logs en tiempo real: flyctl logs --app $APP_NAME -f"
else
  error "El despliegue falló"
fi
