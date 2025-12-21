import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.core.management import call_command
from django.core.serializers import deserialize

# Leer desde stdin
try:
    json_data = sys.stdin.read()
    print(f"Datos recibidos: {len(json_data)} bytes")
    
    # Guardar temporalmente
    with open('/tmp/import_data.json', 'w') as f:
        f.write(json_data)
    
    # Cargar
    call_command('loaddata', '/tmp/import_data.json', verbosity=2)
    print("\n✓ Datos importados correctamente")
    
    # Verificar
    from landing.models import Skill, Experience, Education, Project
    print(f"\nResumen:")
    print(f"  Skills: {Skill.objects.count()}")
    print(f"  Experiencias: {Experience.objects.count()}")
    print(f"  Educación: {Education.objects.count()}")
    print(f"  Proyectos: {Project.objects.count()}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
