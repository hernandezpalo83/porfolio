from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        # Solo páginas públicas con contenido real. Login excluido.
        return ['landing:index', 'blog:post_list']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        priorities = {
            'landing:index': 0.9,
            'blog:post_list': 0.7,
        }
        return priorities.get(item, 0.5)

    def changefreq(self, item):
        freqs = {
            'landing:index': 'weekly',
            'blog:post_list': 'daily',
        }
        return freqs.get(item, 'monthly')