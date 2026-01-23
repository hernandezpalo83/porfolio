from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily' # Tu home cambia a menudo si editas el porfolio

    def items(self):
        # Aquí solo ponemos las páginas que tienen su propia URL real
        return ['landing:index', 'login'] 

    def location(self, item):
        return reverse(item)

# Eliminamos ProjectSitemap si no tienes páginas individuales para cada proyecto.
# Google ya leerá los proyectos al entrar en 'home'.