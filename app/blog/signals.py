"""
TECH-009: Cache invalidation signals para blog.Post.
Cuando se guarda o borra un post se invalida la cache de posts relacionados
de su categoría, y la cache del listado principal.
"""
import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Post

logger = logging.getLogger('app.blog')

_BLOG_LIST_KEY = 'blog_post_list'


def _related_cache_key(category_id):
    return f'related_posts_{category_id}'


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def invalidate_blog_cache(sender, instance, **kwargs):
    """Invalida el listado general y los posts relacionados de la categoría."""
    keys = [_BLOG_LIST_KEY]
    if instance.category_id:
        keys.append(_related_cache_key(instance.category_id))

    deleted = cache.delete_many(keys)
    logger.info(
        "Cache invalidada tras cambio en Post '%s' (categoría %s). Keys: %s",
        instance.title,
        instance.category_id,
        keys,
    )
