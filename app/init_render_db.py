#!/usr/bin/env python3
"""
Script para inicializar la base de datos en Render.com

Este script:
1. Ejecuta migraciones
2. Crea un superuser
3. Carga datos del JSON (opcional)

Ejecutar en Render Shell después del primer deploy:
    python manage.py shell < init_render_db.py
"""

import os
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.app.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection

def check_database():
    """Verifica que la BD está disponible"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Base de datos disponible")
        return True
    except Exception as e:
        print(f"❌ Error al conectar con la BD: {e}")
        return False

def run_migrations():
    """Ejecuta las migraciones pendientes"""
    print("\n🔄 Ejecutando migraciones...")
    try:
        call_command('migrate', verbosity=2)
        print("✅ Migraciones completadas")
        return True
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def create_superuser():
    """Crea un superuser si no existe"""
    print("\n👤 Creando superuser...")
    
    username = 'admin'
    email = 'admin@example.com'
    
    if User.objects.filter(username=username).exists():
        print(f"ℹ️  El usuario '{username}' ya existe")
        return True
    
    try:
        # Usar una contraseña temporal
        password = 'ChangeMeImmediately123!'
        user = User.objects.create_superuser(username, email, password)
        print(f"✅ Superuser creado: {username}")
        print(f"⚠️  Contraseña temporal: {password}")
        print("⚠️  IMPORTANTE: Cambia la contraseña inmediatamente!")
        print("   Ejecuta en Render Shell: python manage.py changepassword admin")
        return True
    except Exception as e:
        print(f"❌ Error al crear superuser: {e}")
        return False

def load_initial_data():
    """Carga datos iniciales si existen"""
    print("\n📦 Buscando datos iniciales...")
    
    json_file = Path('/app/datos_full.json')
    
    if not json_file.exists():
        print("ℹ️  No se encontró datos_full.json")
        print("   Sube el archivo en Render Shell si necesitas cargar datos")
        return True
    
    try:
        print(f"⏳ Cargando datos desde {json_file}...")
        call_command('loaddata', str(json_file), verbosity=2)
        print("✅ Datos cargados exitosamente!")
        return True
    except Exception as e:
        print(f"⚠️  Error al cargar datos: {e}")
        print("   Intenta cargar manualmente después")
        return False

def collect_static():
    """Recolecta archivos estáticos"""
    print("\n📦 Recolectando archivos estáticos...")
    try:
        call_command('collectstatic', '--noinput', '--clear', verbosity=1)
        print("✅ Archivos estáticos recolectados")
        return True
    except Exception as e:
        print(f"⚠️  Error al recolectar estáticos: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 Inicializando Base de Datos para Render.com")
    print("=" * 60)
    
    # Verificar BD
    if not check_database():
        print("❌ No se puede continuar sin acceso a la BD")
        return False
    
    # Ejecutar pasos
    success = True
    success = run_migrations() and success
    success = create_superuser() and success
    success = load_initial_data() and success
    success = collect_static() and success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Inicialización completada exitosamente")
        print("\n📝 Próximos pasos:")
        print("  1. Accede a tu app: https://portfolio.onrender.com")
        print("  2. Ve a /admin")
        print("  3. Inicia sesión con 'admin' y tu contraseña")
        print("  4. Cambia la contraseña inmediatamente")
        print("  5. ¡Disfruta tu portfolio!")
    else:
        print("⚠️  Inicialización completada con advertencias")
        print("   Revisa los errores arriba y corrígelos")
    
    print("=" * 60)
    return success

if __name__ == '__main__':
    main()
