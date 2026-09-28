"""
Privacy-first page analytics that never delays the response.

- No cookies and no stored IP / user-agent: a visitor is an anonymous hash of
  (secret salt, day, IP, user-agent) that changes every day, so sessions and
  bounce rate work without keeping personal data (GDPR data minimisation).
- Country comes from Cloudflare's CF-IPCountry header: no third-party lookups.
- Only successful HTML page views from humans are recorded.
- Writes run after the response is built: in Celery when a broker is configured
  (ANALYTICS_USE_CELERY), otherwise in a small background thread pool.
"""
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.db import close_old_connections
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import PageView, SessionTracker
from .utils import detect_device, get_client_ip, get_country

logger = logging.getLogger(__name__)

EXCLUDED_PREFIXES = (
    '/admin/', '/private/', '/static/', '/media/', '/api/', '/health/', '/.well-known/',
    '/login/', '/logout/', '/csp-report/', '/ckeditor5/', '/blog/feed/',
)
EXCLUDED_PATHS = ('/robots.txt', '/sitemap.xml', '/favicon.ico')
BOT_MARKERS = ('bot', 'crawl', 'spider', 'slurp', 'curl', 'wget', 'python-requests',
               'headless', 'lighthouse', 'pingdom', 'uptime', 'monitor', 'preview')

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='analytics')


def visitor_id(request: HttpRequest) -> str:
    """Anonymous daily visitor hash: same person, same day → same id; nothing reversible is stored."""
    raw = '|'.join((
        settings.SECRET_KEY,
        timezone.now().date().isoformat(),
        get_client_ip(request),
        request.META.get('HTTP_USER_AGENT', ''),
    ))
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def record_pageview(data: dict) -> None:
    """Persist one page view and update its visitor session (runs off the request path)."""
    close_old_connections()
    try:
        session, created = SessionTracker.objects.get_or_create(
            session_id=data['session_id'],
            defaults={
                'country': data['country'],
                'device': data['device'],
                'referrer': data['referrer'],
                'first_page': data['path'],
                'last_page': data['path'],
                'page_count': 1,
            },
        )
        if not created:
            session.last_page = data['path']
            session.page_count += 1
            session.is_bounce = False
            session.save(update_fields=['last_page', 'page_count', 'is_bounce', 'updated_at'])
        PageView.objects.create(**data)
    except Exception:
        logger.exception("Could not record page view for %s", data.get('path'))
    finally:
        close_old_connections()


class AnalyticsTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if self.should_track(request, response):
            self.dispatch(self.build_pageview(request))
        return response

    @staticmethod
    def should_track(request: HttpRequest, response: HttpResponse) -> bool:
        path = request.path
        if request.method != 'GET' or response.status_code != 200:
            return False
        if path in EXCLUDED_PATHS or path.startswith(EXCLUDED_PREFIXES):
            return False
        if not response.get('Content-Type', '').startswith('text/html'):
            return False
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        return bool(user_agent) and not any(marker in user_agent for marker in BOT_MARKERS)

    @staticmethod
    def build_pageview(request: HttpRequest) -> dict:
        return {
            'path': request.path[:500],
            'method': request.method,
            'session_id': visitor_id(request),
            'country': get_country(request),
            'device': detect_device(request.META.get('HTTP_USER_AGENT', '')),
            'referrer': request.META.get('HTTP_REFERER', '')[:500],
            'ip_address': None,
            'user_agent': None,
            'scroll_depth': 0,
            'time_spent': 0,
        }

    @staticmethod
    def dispatch(data: dict) -> None:
        if getattr(settings, 'ANALYTICS_USE_CELERY', False):
            try:
                from app.tasks import record_pageview_task
                record_pageview_task.delay(data)
                return
            except Exception:
                logger.warning("Celery unavailable, recording page view in-process", exc_info=True)
        if getattr(settings, 'ANALYTICS_ASYNC', True):
            _executor.submit(record_pageview, data)
        else:
            record_pageview(data)
