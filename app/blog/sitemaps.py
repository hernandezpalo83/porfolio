from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9  # Prioridad alta para el contenido fresco del blog

    def items(self):
        # Asegúrate de que solo indexamos posts publicados
        return Post.objects.filter(status='published') 

    def lastmod(self, obj):
        # Google valora saber cuándo se actualizó por última vez
        return obj.updated 

    def location(self, obj):
        return obj.get_absolute_url()