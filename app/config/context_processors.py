# tu_app/context_processors.py
from django.conf import settings

def brand_assets(request):
    return {
        'BRAND': settings.PERSONAL_BRAND
    }