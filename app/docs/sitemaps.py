from django.contrib.sitemaps import Sitemap
from .models import Document, Category

class DocumentSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Document.published.all()

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_visible=True)

    def lastmod(self, obj):
        return obj.updated_at
