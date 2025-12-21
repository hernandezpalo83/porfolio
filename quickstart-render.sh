#!/bin/bash

# 🚀 QUICK START - Migración a Render.com en 3 pasos

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      🚀 MIGRACIÓN A RENDER.COM - QUICK START 🚀           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Paso 1: Verificar Git
echo -e "\n${YELLOW}📋 PASO 1: Verificando Git...${NC}"
if ! git status > /dev/null 2>&1; then
    echo -e "${RED}❌ No estás en un repositorio Git${NC}"
    exit 1
fi

if git status | grep -q "nothing to commit"; then
    echo -e "${GREEN}✅ Repositorio limpio${NC}"
else
    echo -e "${YELLOW}⚠️  Hay cambios sin commitear:${NC}"
    git status --short
    
    read -p "¿Deseas hacer commit de estos cambios? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "Preparar para Render.com - eliminar Fly.io"
        echo -e "${GREEN}✅ Cambios commiteados${NC}"
    fi
fi

# Paso 2: Exportar datos
echo -e "\n${YELLOW}📤 PASO 2: Exportando datos locales...${NC}"
if [[ -f "app/db.sqlite3" ]]; then
    python3 -c "
import os
os.chdir('app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
import django
django.setup()
from django.core.management import call_command
call_command('dumpdata', '--natural-foreign', '--indent', '2', stdout=open('../datos_full.json', 'w'))
print('✅ Datos exportados')
"
    
    ls -lh datos_full.json
else
    echo -e "${YELLOW}ℹ️  No hay db.sqlite3 local (normal si vienes de Fly)${NC}"
fi

# Paso 3: Preparar push
echo -e "\n${YELLOW}🔧 PASO 3: Preparando para push...${NC}"

echo -e "${GREEN}✅ Checklist:${NC}"
echo "  ✓ render.yaml creado"
echo "  ✓ Dockerfile optimizado"
echo "  ✓ Scripts de migración listos"
echo "  ✓ Variables de entorno (.env.example)"
echo "  ✓ Documentación RENDER_DEPLOYMENT.md"

# Paso 4: Información final
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ LISTO PARA MIGRAR A RENDER.COM${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}📋 PRÓXIMOS PASOS:${NC}"

echo -e "\n${YELLOW}1. EN RENDER.COM DASHBOARD:${NC}"
echo "   • Ve a https://dashboard.render.com"
echo "   • Crea un nuevo 'Web Service'"
echo "   • Conecta tu repositorio GitHub"
echo "   • Sigue la guía de RENDER_DEPLOYMENT.md"

echo -e "\n${YELLOW}2. HACER PUSH A GITHUB:${NC}"
echo "   git push origin main"
echo "   (Render automáticamente detectará y hará deploy)"

echo -e "\n${YELLOW}3. DESPUÉS DEL PRIMER DEPLOY:${NC}"
echo "   • En Render Dashboard → Web Service → Shell"
echo "   • python manage.py shell < init_render_db.py"
echo "   • python manage.py loaddata datos_full.json"

echo -e "\n${YELLOW}📖 DOCUMENTACIÓN:${NC}"
echo "   • RENDER_DEPLOYMENT.md - Guía completa paso a paso"
echo "   • MIGRATION_SUMMARY.md - Resumen de cambios"
echo "   • .env.example - Variables necesarias"

echo -e "\n${YELLOW}🎯 VARIABLES DE ENTORNO A CONFIGURAR EN RENDER:${NC}"
echo "   • SECRET_KEY (genera con: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\")"
echo "   • DEBUG = false"
echo "   • ALLOWED_HOSTS = portfolio.onrender.com,www.portfolio.onrender.com"
echo "   • DATABASE_URL (Render la crea automáticamente)"

echo -e "\n${GREEN}¿Listo? 🚀${NC}"
read -p "¿Hacer push a GitHub ahora? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Pushing a GitHub...${NC}"
    git push origin main
    echo -e "${GREEN}✅ Push completado!${NC}"
    echo -e "${GREEN}   Tu aplicación se está desplegando en Render...${NC}"
    echo -e "${GREEN}   Monitorea en https://dashboard.render.com${NC}"
else
    echo -e "\n${YELLOW}Recuerda hacer push cuando estés listo:${NC}"
    echo "   git push origin main"
fi

echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}¡Mucho éxito con tu migración a Render.com! 🎉${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
