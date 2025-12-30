
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project # Asegúrate de que este sea el nombre de tu modelo

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        # Nombres de las URLs que quieres indexar
        return ['home'] 

    def location(self, item):
        return reverse(item)

class ProjectSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # Indexa todos los proyectos que tengas en la BD
        return Project.objects.all()

    # Si tu modelo Project tiene un método get_absolute_url(), 
    # no necesitas definir 'location' aquí.