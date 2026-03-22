"""
Landing signals — cache invalidation automática.

Cuando el admin modifica datos que forman parte del bloque 'landing_home_data',
se elimina la caché para que el siguiente request recargue datos frescos.

TTL de la caché: 30 min (ver landing/views.py :: _CACHE_TTL).
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Info, Skill, Experience, Education, Project, Metric, CompanyCollaboration

logger = logging.getLogger(__name__)

_CACHE_KEY = 'landing_home_data'

INVALIDATING_MODELS = (Info, Skill, Experience, Education, Project, Metric, CompanyCollaboration)


def _invalidate_home_cache(sender, **kwargs):
    """Elimina la caché de la landing page."""
    deleted = cache.delete(_CACHE_KEY)
    if deleted:
        logger.info("Cache '%s' invalidada tras cambio en %s", _CACHE_KEY, sender.__name__)
    else:
        logger.debug("Cache '%s' no existía al invalidar desde %s", _CACHE_KEY, sender.__name__)


# Registrar save y delete para todos los modelos que alimentan la landing
for _model in INVALIDATING_MODELS:
    post_save.connect(_invalidate_home_cache, sender=_model)
    post_delete.connect(_invalidate_home_cache, sender=_model)
