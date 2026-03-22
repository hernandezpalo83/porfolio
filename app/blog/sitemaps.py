from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Category


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.publish

    def location(self, obj):
        return obj.get_absolute_url()


class BlogCategorySitemap(Sitemap):
    """Sitemap de categorías del blog — indexa /blog/<slug>/ para crawlers."""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        # Solo categorías que tienen al menos un post publicado
        return Category.objects.filter(posts__status='published').distinct()

    def lastmod(self, obj):
        # Fecha del post más reciente de la categoría
        latest = obj.posts.filter(status='published').order_by('-publish').first()
        return latest.publish if latest else None

    def location(self, obj):
        return reverse('blog:post_list_by_category', args=[obj.slug])