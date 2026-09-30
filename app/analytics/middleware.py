"""
Privacy-first analytics of the public pages, focused on who is looking at the
portfolio (companies, returning visitors, channel) without delaying responses.

- No cookies and no stored IP / user-agent. Two anonymous, non-reversible hashes
  of (secret salt, period, IP, user-agent): a daily one groups a session and a
  monthly one recognises a returning visitor on the same device and network.
- The owner of the network (company, university, operator...) is resolved
  offline from the IP in a background thread (see network.py); the IP is kept
  in memory only for that lookup.
- Own channels: ?src=linkedin / firma / cv (Channel rows) are attributed to the
  whole session and to later visits of the same visitor that month.
- Country comes from Cloudflare's CF-IPCountry header.
- Only successful HTML page views from humans are recorded; logged-in users
  (the site owner) and the private area are never tracked.
- Writes run after the response is built: in Celery when a broker is configured
  (ANALYTICS_USE_CELERY), otherwise in a small background thread pool.
"""
import hashlib
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.db import close_old_connections
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import Channel, Event, PageView, SessionTracker, TrafficSource
from .network import lookup
from .sources import classify_source
from .utils import detect_device, get_client_ip, get_country

logger = logging.getLogger(__name__)

EXCLUDED_PREFIXES = (
    '/admin/', '/private/', '/static/', '/media/', '/api/', '/health/', '/.well-known/',
    '/login/', '/logout/', '/accounts/', '/csp-report/', '/ckeditor5/', '/blog/feed/', '/a/',
    '/gym/', '/prompts/', '/metadata/',
)
EXCLUDED_PATHS = ('/robots.txt', '/sitemap.xml', '/favicon.ico')
BOT_MARKERS = ('bot', 'crawl', 'spider', 'slurp', 'curl', 'wget', 'python-requests',
               'headless', 'lighthouse', 'pingdom', 'uptime', 'monitor', 'preview')

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='analytics')


def _anonymous_hash(request: HttpRequest, period: str) -> str:
    raw = '|'.join((settings.SECRET_KEY, period, get_client_ip(request), request.META.get('HTTP_USER_AGENT', '')))
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def visitor_id(request: HttpRequest) -> str:
    """Anonymous daily id: groups the pages of one visit (session)."""
    return _anonymous_hash(request, timezone.now().date().isoformat())


def monthly_visitor_id(request: HttpRequest) -> str:
    """Anonymous monthly id: same device and network during the month → same visitor."""
    return _anonymous_hash(request, 'm' + timezone.now().strftime('%Y-%m'))


def is_human_visitor(request: HttpRequest) -> bool:
    """A real browser that is not the logged-in owner of the site."""
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        return False
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    return bool(user_agent) and not any(marker in user_agent for marker in BOT_MARKERS)


def is_trackable_request(request: HttpRequest) -> bool:
    path = request.path
    if path in EXCLUDED_PATHS or path.startswith(EXCLUDED_PREFIXES):
        return False
    return is_human_visitor(request)


def visit_context(request: HttpRequest) -> dict:
    """Identity of the visit shared by page views and events (the IP stays in memory only)."""
    return {
        'session_id': visitor_id(request),
        'visitor_id': monthly_visitor_id(request),
        '_ip': get_client_ip(request),
    }


def _resolve_network(data: dict) -> None:
    info = lookup(data.pop('_ip', ''))
    data['asn'] = info.asn
    data['organization'] = info.organization
    data['network_type'] = info.network_type


def _attributed_channel(data: dict, session: SessionTracker | None) -> Channel | None:
    """Channel of this visit, else of its session, else of an earlier visit by the same visitor this month."""
    code = data.pop('_channel_code', '')
    if code:
        channel = Channel.objects.filter(code=code).first()
        if channel:
            return channel
    if session and session.channel_id:
        return session.channel
    earlier = (PageView.objects.filter(visitor_id=data['visitor_id'], channel__isnull=False)
               .select_related('channel').order_by('-timestamp').first())
    return earlier.channel if earlier else None


def record_pageview(data: dict) -> None:
    """Persist one page view and update its session (runs off the request path)."""
    close_old_connections()
    try:
        _resolve_network(data)
        session = SessionTracker.objects.filter(session_id=data['session_id']).first()
        channel = _attributed_channel(data, session)
        data['channel'] = channel
        if channel and data['source'] in (TrafficSource.DIRECT, TrafficSource.INTERNAL):
            data['source'] = TrafficSource.CHANNEL

        if session is None:
            SessionTracker.objects.create(
                session_id=data['session_id'], visitor_id=data['visitor_id'],
                country=data['country'], device=data['device'], referrer=data['referrer'],
                first_page=data['path'], last_page=data['path'], page_count=1,
                source=data['source'], channel=channel,
                organization=data['organization'], network_type=data['network_type'],
            )
        else:
            session.last_page = data['path']
            session.page_count += 1
            session.is_bounce = False
            fields = ['last_page', 'page_count', 'is_bounce', 'updated_at']
            if channel and not session.channel_id:
                session.channel = channel
                fields.append('channel')
            session.save(update_fields=fields)
        PageView.objects.create(**data)
    except Exception:
        logger.exception("Could not record page view for %s", data.get('path'))
    finally:
        close_old_connections()


def record_event_data(data: dict) -> None:
    """Persist one event, inheriting network and channel from its session."""
    close_old_connections()
    try:
        _resolve_network(data)
        session = SessionTracker.objects.filter(session_id=data['session_id']).select_related('channel').first()
        data['channel'] = session.channel if session else None
        Event.objects.create(**data)
    except Exception:
        logger.exception("Could not record event %s", data.get('kind'))
    finally:
        close_old_connections()


def dispatch(func, data: dict) -> None:
    """Run a recorder off the request path (Celery if configured, else a thread; inline in tests)."""
    if getattr(settings, 'ANALYTICS_USE_CELERY', False):
        try:
            from app.tasks import record_analytics_task
            record_analytics_task.delay(func.__name__, data)
            return
        except Exception:
            logger.warning("Celery unavailable, recording analytics in-process", exc_info=True)
    if getattr(settings, 'ANALYTICS_ASYNC', True):
        _executor.submit(func, data)
    else:
        func(data)


def record_event(request: HttpRequest, kind: str, label: str = '', path: str = '') -> None:
    """Server-side events (contact form sent, newsletter sign-up...)."""
    if not is_human_visitor(request):
        return
    dispatch(record_event_data, {
        **visit_context(request),
        'kind': kind, 'label': label[:200], 'path': (path or request.path)[:500],
    })


class AnalyticsTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Known before rendering so the page can send reading time back (<body data-pv>)
        request.analytics_pageview_id = uuid.uuid4()
        response = self.get_response(request)
        if self.should_track(request, response):
            dispatch(record_pageview, self.build_pageview(request))
        return response

    @staticmethod
    def should_track(request: HttpRequest, response: HttpResponse) -> bool:
        if request.method != 'GET' or response.status_code != 200:
            return False
        if not response.get('Content-Type', '').startswith('text/html'):
            return False
        return is_trackable_request(request)

    @staticmethod
    def build_pageview(request: HttpRequest) -> dict:
        channel_code = request.GET.get('src', '')[:40]
        origin = classify_source(
            request.META.get('QUERY_STRING', ''),
            request.META.get('HTTP_REFERER', ''),
            own_host=request.get_host().split(':')[0].removeprefix('www.'),
            has_channel=bool(channel_code),
        )
        return {
            **visit_context(request),
            **origin,
            '_channel_code': channel_code,
            'pageview_id': str(request.analytics_pageview_id),
            'path': request.path[:500],
            'method': request.method,
            'country': get_country(request),
            'device': detect_device(request.META.get('HTTP_USER_AGENT', '')),
            'referrer': request.META.get('HTTP_REFERER', '')[:500],
            'ip_address': None,
            'user_agent': None,
            'scroll_depth': 0,
            'time_spent': 0,
        }
