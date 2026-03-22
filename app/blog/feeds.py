"""
TECH-008: RSS Feed del blog usando django.contrib.syndication.
URL: /blog/feed/
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed

from .models import Post


class LatestPostsFeed(Feed):
    title = "Blog — Javier Hernández Martín"
    description = "Artículos sobre Product Management técnico, Django y desarrollo de software."
    author_name = "Javier Hernández Martín"
    feed_copyright = "Javier Hernández Martín"

    def link(self):
        return reverse('blog:post_list')

    def items(self):
        return Post.objects.filter(status='published').order_by('-publish')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.meta_description or item.excerpt

    def item_pubdate(self, item):
        return item.publish

    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return self.author_name


class LatestPostsAtomFeed(LatestPostsFeed):
    """Versión Atom del feed (mejor soporte para clientes modernos)."""
    feed_type = Atom1Feed
    subtitle = LatestPostsFeed.description
