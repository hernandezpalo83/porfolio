import logging
import uuid
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.http import HttpRequest
from .models import PageView, SessionTracker
from .utils import get_client_ip, detect_device, get_country_from_ip

logger = logging.getLogger(__name__)


class AnalyticsTrackingMiddleware(MiddlewareMixin):
    """
    Middleware que captura cada vista de página (privacy-first, sin cookies).
    Registra: path, país, dispositivo, referrer, duración, scroll depth.
    """

    EXCLUDED_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
        '/api/',
        '/health/',
        '/.well-known/',
    ]

    def should_track(self, request: HttpRequest) -> bool:
        """Determina si se debe trackear esta solicitud."""
        path = request.path

        # Excluir paths administrativos
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return False

        # Solo GET
        if request.method != 'GET':
            return False

        return True

    def process_request(self, request: HttpRequest):
        """Al iniciar la solicitud: capturar metadata."""
        if not self.should_track(request):
            return None

        # Generar o recuperar session_id (sin cookies)
        session_id = request.META.get('HTTP_X_SESSION_ID')
        if not session_id:
            session_id = str(uuid.uuid4())

        request._analytics_session_id = session_id
        request._analytics_timestamp = timezone.now()
        request._analytics_referrer = request.META.get('HTTP_REFERER', '')
        request._analytics_country = get_country_from_ip(get_client_ip(request))
        request._analytics_device = detect_device(request.META.get('HTTP_USER_AGENT', ''))
        request._analytics_ip = get_client_ip(request)
        request._analytics_user_agent = request.META.get('HTTP_USER_AGENT', '')

        return None

    def process_response(self, request: HttpRequest, response):
        """Al terminar la solicitud: registrar en PageView."""
        if not hasattr(request, '_analytics_session_id'):
            return response

        if response.status_code not in [200, 304]:
            return response

        try:
            # Security: Truncar path en 500 caracteres para evitar inyección
            path = request.path[:500]
            PageView.objects.create(
                path=path,
                method=request.method,
                session_id=request._analytics_session_id,
                country=request._analytics_country,
                device=request._analytics_device,
                referrer=request._analytics_referrer[:500] if request._analytics_referrer else '',
                ip_address=request._analytics_ip,
                user_agent=request._analytics_user_agent[:200],
                scroll_depth=0,
                time_spent=0,
            )

            # Actualizar o crear SessionTracker
            session, created = SessionTracker.objects.get_or_create(
                session_id=request._analytics_session_id,
                defaults={
                    'country': request._analytics_country,
                    'device': request._analytics_device,
                    'referrer': request._analytics_referrer[:500] if request._analytics_referrer else '',
                    'first_page': request.path,
                    'last_page': request.path,
                    'page_count': 1,
                }
            )

            if not created:
                session.last_page = request.path
                session.page_count += 1
                session.is_bounce = (session.page_count == 1)
                session.save(update_fields=['last_page', 'page_count', 'is_bounce', 'updated_at'])

        except Exception as e:
            logger.error(f"Error en AnalyticsTrackingMiddleware: {e}", exc_info=True)

        return response
