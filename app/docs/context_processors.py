from .models import Category, Document

def docs_navigation(request):
    """Context processor to provide global docs navigation data"""
    # Only run on /docs/ paths to avoid overhead elsewhere
    if request.path.startswith('/docs/'):
        return {
            'all_categories': Category.objects.filter(is_visible=True),
            'recent_docs': Document.published.recent()
        }
    return {}
