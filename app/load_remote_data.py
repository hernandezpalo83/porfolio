#!/usr/bin/env python
"""
Script para cargar datos desde stdin en la base de datos remota.
Uso local: cat datos.json | python load_remote_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.core.management import call_command
from landing.models import Skill, Experience, Education, Project, Info, Contact

def main():
    try:
        # Leer JSON desde stdin
        json_data = sys.stdin.read()
        
        if not json_data.strip():
            print("✗ No se recibieron datos")
            sys.exit(1)
        
        print(f"📥 Datos recibidos: {len(json_data)} bytes")
        
        # Guardar a archivo temporal
        temp_file = '/tmp/import_data_temp.json'
        with open(temp_file, 'w') as f:
            f.write(json_data)
        
        print("⏳ Cargando datos...")
        call_command('loaddata', temp_file, verbosity=1)
        
        # Limpiar archivo temporal
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # Mostrar resumen
        print("\n✓ Datos importados correctamente")
        print("\n📊 Resumen de datos cargados:")
        print(f"   Skills: {Skill.objects.count()}")
        print(f"   Experiencias: {Experience.objects.count()}")
        print(f"   Educación: {Education.objects.count()}")
        print(f"   Proyectos: {Project.objects.count()}")
        print(f"   Contactos: {Contact.objects.count()}")
        print(f"   Info: {Info.objects.count()}")
        
    except Exception as e:
        print(f"✗ Error al importar datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
