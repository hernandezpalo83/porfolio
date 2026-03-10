# tu_app/context_processors.py
from django.conf import settings

def brand_assets(request):
    return {
        'BRAND': getattr(settings, 'PERSONAL_BRAND', {}),
        'BRAND_ASSETS_URL': getattr(settings, 'BRAND_ASSETS_URL', '')
    }