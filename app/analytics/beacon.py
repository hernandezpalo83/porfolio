"""
Public endpoint for the reading metrics and events sent by the browser
(landing/js/insights.js) with navigator.sendBeacon. No cookies, no CSRF token
(sendBeacon cannot send one), rate-limited and strictly validated.
"""
import json
import logging
import uuid

from django.db import close_old_connections
from django.db.models import F
from django.db.models.functions import Greatest
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .middleware import dispatch, is_human_visitor, record_event
from .models import Event, PageView

logger = logging.getLogger(__name__)

CLIENT_EVENTS = {Event.Kind.CV_DOWNLOAD, Event.Kind.OUTBOUND, Event.Kind.CASE_OPEN, Event.Kind.FILTER}
MAX_BODY = 4096
MAX_SECONDS = 60 * 60


def record_reading(data: dict) -> None:
    """Keep the highest time and scroll reported for a page view (several beacons per page)."""
    close_old_connections()
    try:
        PageView.objects.filter(pageview_id=data['pageview_id']).update(
            time_spent=Greatest(F('time_spent'), data['seconds']),
            scroll_depth=Greatest(F('scroll_depth'), data['scroll']),
        )
    except Exception:
        logger.exception("Could not store reading metrics")
    finally:
        close_old_connections()


def _int(value, low: int, high: int) -> int:
    try:
        return max(low, min(high, int(value)))
    except (TypeError, ValueError):
        return low


@csrf_exempt
@require_POST
@ratelimit(key='ip', rate='120/m', block=True)
def beacon(request: HttpRequest) -> HttpResponse:
    if len(request.body) > MAX_BODY or not is_human_visitor(request):
        return HttpResponse(status=204)
    try:
        payload = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=400)
    if not isinstance(payload, dict):
        return HttpResponse(status=400)

    kind = payload.get('type')
    if kind == 'read':
        try:
            pageview_id = str(uuid.UUID(str(payload.get('pv'))))
        except ValueError:
            return HttpResponse(status=400)
        dispatch(record_reading, {
            'pageview_id': pageview_id,
            'seconds': _int(payload.get('t'), 0, MAX_SECONDS),
            'scroll': _int(payload.get('s'), 0, 100),
        })
    elif kind == 'event' and payload.get('kind') in CLIENT_EVENTS:
        record_event(request, payload['kind'], str(payload.get('label', ''))[:200],
                     path=str(payload.get('path', ''))[:500])
    else:
        return HttpResponse(status=400)
    return HttpResponse(status=204)
