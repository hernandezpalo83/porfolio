from django.conf import settings

def components_context(request):
    """
    Inyecta variables globales de configuración en el contexto de plantilla.
    """
    config = getattr(settings, 'COMPONENTS_UI_CONFIG', {})
    
    return {
        'GLOBAL_COLORS': {
            'PRIMARY': config.get('PRIMARY_COLOR', '#2563eb'),
            'SECONDARY': config.get('SECONDARY_COLOR', '#c026d3'),
        },
        'GLOBAL_ICONS': config.get('ICONS_CDN', 'heroicons'),
        'USER_LOCALE': config.get('LOCALE', 'es'),
        'ENABLE_ANIMATIONS': config.get('ENABLE_ANIMATIONS', True),
        'ENABLE_DARK_MODE': config.get('ENABLE_DARK_MODE', False),
    }
