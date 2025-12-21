#!/usr/bin/env python3
"""
Script para migrar datos a Render.com

Este script toma el JSON exportado desde SQLite local y lo carga
en la base de datos PostgreSQL de Render.

Uso:
    python migrate_to_render.py datos_full.json

Requisitos:
    - Tener psycopg2-binary instalado
    - Variables de entorno configuradas (DATABASE_URL)
    - El archivo JSON debe existir
"""

import os
import json
import sys
import django
import base64
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.core.management import call_command
from django.core.serializers import deserialize
from django.db import transaction


def load_json_data(json_file):
    """
    Carga datos JSON en la base de datos PostgreSQL de Render
    
    Args:
        json_file (str): Ruta al archivo JSON
    """
    if not os.path.exists(json_file):
        print(f"❌ Error: El archivo {json_file} no existe")
        return False
    
    file_size = os.path.getsize(json_file)
    print(f"📦 Tamaño del archivo: {file_size / 1024:.2f} KB")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Archivo JSON cargado: {len(data)} objetos encontrados")
        
        # Cargar datos usando Django
        with transaction.atomic():
            print("⏳ Cargando datos en la base de datos...")
            call_command('loaddata', json_file, verbosity=2)
            
        print("✅ Datos cargados exitosamente!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error durante la carga: {e}")
        return False


def export_local_data(output_file='datos_full.json'):
    """
    Exporta datos desde SQLite local a JSON
    
    Args:
        output_file (str): Nombre del archivo de salida
    """
    print(f"📤 Exportando datos locales a {output_file}...")
    
    try:
        call_command('dumpdata', '--natural-foreign', '--indent', '2', 
                    stdout=open(output_file, 'w'))
        
        file_size = os.path.getsize(output_file)
        print(f"✅ Datos exportados: {file_size / 1024:.2f} KB")
        
        # Crear versión en base64
        with open(output_file, 'rb') as f:
            data = f.read()
        
        b64_file = output_file.replace('.json', '.b64')
        with open(b64_file, 'w') as f:
            f.write(base64.b64encode(data).decode('utf-8'))
        
        print(f"✅ Versión base64 creada: {b64_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Error al exportar datos: {e}")
        return None


def create_superuser():
    """Crea un superuser si no existe"""
    from django.contrib.auth.models import User
    
    username = 'admin'
    email = 'admin@example.com'
    password = 'change_me_in_production'
    
    if User.objects.filter(username=username).exists():
        print(f"ℹ️  El usuario {username} ya existe")
    else:
        User.objects.create_superuser(username, email, password)
        print(f"✅ Superuser creado: {username}")
        print(f"⚠️  IMPORTANTE: Cambia la contraseña en producción!")


def main():
    """Función principal"""
    print("🚀 Script de Migración de Datos para Render.com")
    print("=" * 60)
    
    # Opciones
    if len(sys.argv) > 1:
        if sys.argv[1] == '--export':
            # Exportar datos locales
            export_local_data()
        elif sys.argv[1] == '--load':
            # Cargar datos
            json_file = sys.argv[2] if len(sys.argv) > 2 else 'datos_full.json'
            load_json_data(json_file)
        elif sys.argv[1] == '--full':
            # Ejecutar migraciones + crear superuser
            print("\n1️⃣  Ejecutando migraciones...")
            call_command('migrate', verbosity=2)
            
            print("\n2️⃣  Creando superuser...")
            create_superuser()
            
            print("\n3️⃣  Cargando datos...")
            json_file = sys.argv[2] if len(sys.argv) > 2 else 'datos_full.json'
            load_json_data(json_file)
        else:
            print(f"❌ Opción desconocida: {sys.argv[1]}")
    else:
        # Mostrar ayuda
        print("""
Opciones disponibles:

  python migrate_to_render.py --export
    → Exporta datos de SQLite local a JSON

  python migrate_to_render.py --load [archivo.json]
    → Carga datos JSON en PostgreSQL

  python migrate_to_render.py --full [archivo.json]
    → Ejecuta migraciones + crear superuser + cargar datos

Ejemplo:
  python migrate_to_render.py --full datos_full.json
        """)


if __name__ == '__main__':
    main()
