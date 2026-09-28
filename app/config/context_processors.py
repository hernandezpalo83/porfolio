# app/config/context_processors.py
from django.conf import settings


def brand_assets(request):
    """Context processor para assets y branding global."""
    return {
        'BRAND': getattr(settings, 'PERSONAL_BRAND', {}),
        'BRAND_ASSETS_URL': getattr(settings, 'BRAND_ASSETS_URL', ''),
        'SITE_URL': getattr(settings, 'SITE_URL', ''),
    }


def csp_nonce(request):
    """
    Context processor para pasar el nonce de CSP a los templates.

    Generado por CSPNonceMiddleware. Usar en templates como:
        <script nonce="{{ request.csp_nonce }}">...</script>

    También disponible como variable de contexto:
        {{ csp_nonce }}
    """
    return {
        'csp_nonce': getattr(request, 'csp_nonce', '')
    }