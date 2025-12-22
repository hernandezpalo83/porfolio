import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # Ajusta si tu settings está en otra ruta
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Cambia los valores por tus datos
username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@porfolio.hernandezpalo.es')
password = os.environ.get('ADMIN_PASSWORD', 'admin1234')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created")
else:
    print("Superuser already exists")
