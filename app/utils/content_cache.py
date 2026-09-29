"""
Versioned cache for public content (landing, blog, wiki).

Every cached value lives under a group version: saving or deleting any model of
the group from the admin bumps the version, so all its keys become stale at once
in every gunicorn worker (the cache backend is shared, see settings.CACHES).

    posts = cached(('blog',), 'published_posts', lambda: list(Post.objects...))
    register('blog', Post, Category)   # in AppConfig.ready()
"""
import logging
import time
from typing import Any, Callable, Iterable

from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save

logger = logging.getLogger(__name__)

DEFAULT_TTL = 60 * 60
_VERSION_KEY = 'content:{group}:version'


def _version(group: str) -> int:
    key = _VERSION_KEY.format(group=group)
    version = cache.get(key)
    if version is None:
        # A timestamp (not 1) so a cache wipe can never resurrect old keys
        version = int(time.time() * 1000)
        cache.set(key, version, None)
    return version


def cached(groups: Iterable[str], key: str, builder: Callable[[], Any], ttl: int = DEFAULT_TTL) -> Any:
    """Return the cached value, building it once per group version. None is never cached."""
    versions = '.'.join(f'{g}{_version(g)}' for g in groups)
    full_key = f'content:{versions}:{key}'
    value = cache.get(full_key)
    if value is None:
        value = builder()
        if value is not None:
            cache.set(full_key, value, ttl)
    return value


def invalidate(group: str) -> None:
    cache.set(_VERSION_KEY.format(group=group), int(time.time() * 1000), None)
    logger.info("Content cache '%s' invalidated", group)


def register(group: str, *models) -> None:
    """Invalidate the group whenever one of these models (or its M2M relations) changes."""
    def handler(sender, **kwargs):
        invalidate(group)

    for model in models:
        uid = f'content-cache-{group}-{model._meta.label}'
        post_save.connect(handler, sender=model, weak=False, dispatch_uid=uid + '-save')
        post_delete.connect(handler, sender=model, weak=False, dispatch_uid=uid + '-delete')
        for field in model._meta.many_to_many:
            m2m_changed.connect(handler, sender=field.remote_field.through, weak=False,
                                dispatch_uid=f'{uid}-m2m-{field.name}')
