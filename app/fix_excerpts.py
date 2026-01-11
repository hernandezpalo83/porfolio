import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings') # Cambia 'tu_proyecto' por el nombre real
django.setup()

from blog.models import Post

posts = Post.objects.all()
for p in posts:
    p.save() # Esto disparará la lógica del nuevo método save()
    print(f"Resumen generado para: {p.title}")