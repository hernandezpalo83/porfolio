from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        # Filtramos por publicados
        return Post.objects.filter(status='published') 

    def lastmod(self, obj):
        # Usamos 'publish' que sí existe en tu modelo
        return obj.publish 

    def location(self, obj):
        return obj.get_absolute_url()