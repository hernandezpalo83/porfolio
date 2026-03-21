from django.core.cache import cache
from .models import Category, Document


def docs_navigation(request):
    """Context processor to provide global docs navigation data (cached 10 min)."""
    if not request.path.startswith('/wiki/'):
        return {}

    cache_key = 'docs_navigation_data'
    nav_data = cache.get(cache_key)
    if nav_data is None:
        nav_data = {
            'all_categories': list(Category.objects.filter(is_visible=True).order_by('order')),
            'recent_docs': list(Document.published.recent()),
        }
        cache.set(cache_key, nav_data, 60 * 10)

    return nav_data
