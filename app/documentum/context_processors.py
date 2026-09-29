from app.utils.content_cache import cached
from .models import Category, Document
import logging

logger = logging.getLogger(__name__)


def docs_navigation(request):
    """Context processor to provide global docs navigation data (cached 10 min). Gracefully handles DB errors."""
    if not request.path.startswith('/wiki/'):
        return {}

    try:
        nav_data = cached(('wiki',), 'navigation', lambda: {
            'all_categories': list(Category.objects.filter(is_visible=True).order_by('order')),
            'recent_docs': list(Document.published.recent()),
        })

        return nav_data
    except Exception as e:
        logger.error(f"Error loading docs_navigation: {str(e)}", exc_info=True)
        return {}
