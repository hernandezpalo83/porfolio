"""
Recruiter insights: who is looking at the portfolio and what they do.

Everything is computed from anonymous PageView / SessionTracker / Event rows
of the public pages. Networks are grouped by ASN, and NetworkLabel rows edited
in the admin rename or reclassify them retroactively.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import timedelta

from django.db.models import Avg, Count, Max, Min, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Channel, Event, NetworkLabel, NetworkType, PageView, TrafficSource

PERIODS = (7, 30, 90)
# Networks that point to a company or institution (the audience of the portfolio)
ORGANIZATION_TYPES = (NetworkType.BUSINESS, NetworkType.CORPORATE_PROXY, NetworkType.EDUCATION,
                      NetworkType.GOVERNMENT)
PRIVATE_TYPES = (NetworkType.ISP, NetworkType.MOBILE)
EVENT_ICONS = {
    Event.Kind.CV_DOWNLOAD: 'bi-file-earmark-arrow-down',
    Event.Kind.CONTACT_SUBMIT: 'bi-envelope-check',
    Event.Kind.NEWSLETTER: 'bi-newspaper',
    Event.Kind.OUTBOUND: 'bi-box-arrow-up-right',
    Event.Kind.CASE_OPEN: 'bi-briefcase',
    Event.Kind.FILTER: 'bi-funnel',
}


@dataclass
class Organization:
    key: str
    asn: int | None
    name: str
    network_type: str
    visits: int = 0
    visitors: int = 0
    days: int = 0
    pages: int = 0
    reading_seconds: int = 0
    first_seen: object = None
    last_seen: object = None
    channels: list = field(default_factory=list)
    events: Counter = field(default_factory=Counter)

    @property
    def type_label(self) -> str:
        return NetworkType(self.network_type).label

    @property
    def conversions(self) -> int:
        return sum(self.events[k] for k in Event.CONVERSIONS)

    @property
    def is_returning(self) -> bool:
        return self.days > 1

    @property
    def interest(self) -> int:
        """Rough score to sort organizations: return visits, reading and conversions weigh most."""
        return (self.visits + 3 * max(self.days - 1, 0) + self.reading_seconds // 60
                + 5 * self.events[Event.Kind.CASE_OPEN] + 15 * self.conversions)


def period_from(request) -> int:
    try:
        days = int(request.GET.get('days', 30))
    except ValueError:
        days = 30
    return days if days in PERIODS else 30


def _labels() -> dict[int, NetworkLabel]:
    return {label.asn: label for label in NetworkLabel.objects.all()}


def _name(asn, organization, network_type, labels):
    label = labels.get(asn)
    if label:
        return label.name, label.network_type
    return organization or 'Red desconocida', network_type


def _org_key(asn, organization) -> str:
    return f'as{asn}' if asn else f'name:{organization}'


def build(days: int, include_datacenters: bool = False) -> dict:
    since = timezone.now() - timedelta(days=days)
    labels = _labels()
    views = PageView.objects.filter(timestamp__gte=since)
    events = Event.objects.filter(timestamp__gte=since)
    if not include_datacenters:
        views = views.exclude(network_type=NetworkType.HOSTING)
        events = events.exclude(network_type=NetworkType.HOSTING)

    # --- KPIs ---
    visitor_days = (views.exclude(visitor_id='').values('visitor_id')
                    .annotate(n=Count(TruncDate('timestamp'), distinct=True)))
    returning = sum(1 for row in visitor_days if row['n'] > 1)
    reading = views.filter(time_spent__gt=0).aggregate(avg=Avg('time_spent'))['avg'] or 0

    # --- Organizations (grouped by network) ---
    orgs: dict[str, Organization] = {}
    rows = (views.values('asn', 'organization', 'network_type')
            .annotate(visits=Count('id'), visitors=Count('visitor_id', distinct=True),
                      days=Count(TruncDate('timestamp'), distinct=True), pages=Count('path', distinct=True),
                      first=Min('timestamp'), last=Max('timestamp')))
    for row in rows:
        name, kind = _name(row['asn'], row['organization'], row['network_type'], labels)
        key = _org_key(row['asn'], row['organization'])
        org = orgs.setdefault(key, Organization(key=key, asn=row['asn'], name=name, network_type=kind))
        org.visits += row['visits']
        org.visitors += row['visitors']
        org.days = max(org.days, row['days'])
        org.pages = max(org.pages, row['pages'])
        org.first_seen = min(filter(None, [org.first_seen, row['first']]))
        org.last_seen = max(filter(None, [org.last_seen, row['last']]))

    for row in views.values('asn', 'organization').annotate(t=Count('id'), s=Avg('time_spent')):
        org = orgs.get(_org_key(row['asn'], row['organization']))
        if org:
            org.reading_seconds += int((row['s'] or 0) * row['t'])
    for row in (views.filter(channel__isnull=False).values('asn', 'organization', 'channel__name')
                .distinct()):
        org = orgs.get(_org_key(row['asn'], row['organization']))
        if org and row['channel__name'] not in org.channels:
            org.channels.append(row['channel__name'])
    for row in events.values('asn', 'organization', 'kind').annotate(n=Count('id')):
        org = orgs.get(_org_key(row['asn'], row['organization']))
        if org:
            org.events[row['kind']] += row['n']

    organizations = sorted((o for o in orgs.values() if o.network_type in ORGANIZATION_TYPES),
                           key=lambda o: (o.interest, o.last_seen), reverse=True)
    private_visits = sum(o.visits for o in orgs.values() if o.network_type in PRIVATE_TYPES)
    private_visitors = sum(o.visitors for o in orgs.values() if o.network_type in PRIVATE_TYPES)

    # --- Channels and sources ---
    channel_rows = {c.pk: {'channel': c, 'visits': 0, 'visitors': 0, 'conversions': 0}
                    for c in Channel.objects.all()}
    for row in (views.filter(channel__isnull=False).values('channel')
                .annotate(visits=Count('id'), visitors=Count('visitor_id', distinct=True))):
        channel_rows[row['channel']].update(visits=row['visits'], visitors=row['visitors'])
    for row in (events.filter(channel__isnull=False, kind__in=Event.CONVERSIONS).values('channel')
                .annotate(n=Count('id'))):
        channel_rows[row['channel']]['conversions'] = row['n']

    entries = views.exclude(source=TrafficSource.INTERNAL)
    sources = [{'label': TrafficSource(r['source']).label, 'visits': r['n']}
               for r in entries.values('source').annotate(n=Count('id')).order_by('-n')]
    referrers = list(entries.exclude(referrer_domain='').values('referrer_domain')
                     .annotate(n=Count('id')).order_by('-n')[:10])
    campaigns = list(views.exclude(utm_campaign='', utm_source='')
                     .values('utm_source', 'utm_campaign').annotate(n=Count('id')).order_by('-n')[:10])

    # --- Content ---
    pages = list(views.values('path').annotate(
        visits=Count('id'), visitors=Count('visitor_id', distinct=True),
        avg_time=Avg('time_spent', filter=Q(time_spent__gt=0)), avg_scroll=Avg('scroll_depth', filter=Q(scroll_depth__gt=0)),
    ).order_by('-visits')[:15])
    cases = list(events.filter(kind=Event.Kind.CASE_OPEN).values('label').annotate(n=Count('id')).order_by('-n'))
    outbound = list(events.filter(kind=Event.Kind.OUTBOUND).values('label').annotate(n=Count('id')).order_by('-n')[:10])

    # --- Returning visitors (anonymous monthly id) ---
    returning_ids = [r['visitor_id'] for r in visitor_days if r['n'] > 1]
    returning_rows = []
    if returning_ids:
        stats = (views.filter(visitor_id__in=returning_ids).values('visitor_id')
                 .annotate(visits=Count('id'), days=Count(TruncDate('timestamp'), distinct=True),
                           last=Max('timestamp'), reading=Avg('time_spent')))
        latest = {}
        for pv in (views.filter(visitor_id__in=returning_ids).order_by('visitor_id', '-timestamp')
                   .values('visitor_id', 'asn', 'organization', 'network_type', 'channel__name')):
            latest.setdefault(pv['visitor_id'], pv)
        conv = Counter(events.filter(visitor_id__in=returning_ids, kind__in=Event.CONVERSIONS)
                       .values_list('visitor_id', flat=True))
        for row in stats:
            pv = latest[row['visitor_id']]
            name, kind = _name(pv['asn'], pv['organization'], pv['network_type'], labels)
            returning_rows.append({**row, 'alias': row['visitor_id'][:6], 'organization': name,
                                   'type_label': NetworkType(kind).label, 'channel': pv['channel__name'],
                                   'conversions': conv[row['visitor_id']]})
        returning_rows.sort(key=lambda r: (r['days'], r['visits']), reverse=True)

    # --- Daily chart ---
    per_day = defaultdict(lambda: {'visits': 0, 'visitors': 0, 'organizations': 0})
    for row in views.annotate(day=TruncDate('timestamp')).values('day').annotate(
            visits=Count('id'), visitors=Count('visitor_id', distinct=True),
            organizations=Count('asn', distinct=True, filter=Q(network_type__in=ORGANIZATION_TYPES))):
        per_day[row['day']] = row
    today = timezone.localdate()
    chart = [{'day': (today - timedelta(days=i)).isoformat(),
              'visits': per_day[today - timedelta(days=i)]['visits'],
              'visitors': per_day[today - timedelta(days=i)]['visitors'],
              'organizations': per_day[today - timedelta(days=i)]['organizations']}
             for i in range(days - 1, -1, -1)]

    # --- Recent activity of organizations ---
    activity = []
    for ev in (events.filter(network_type__in=ORGANIZATION_TYPES).select_related('channel')[:25]):
        name, _ = _name(ev.asn, ev.organization, ev.network_type, labels)
        activity.append({'when': ev.timestamp, 'organization': name, 'org_key': _org_key(ev.asn, ev.organization),
                         'kind': ev.get_kind_display(), 'icon': EVENT_ICONS.get(ev.kind, 'bi-dot'),
                         'label': ev.label, 'channel': ev.channel.name if ev.channel else ''})

    conversions = Counter(dict(events.filter(kind__in=Event.CONVERSIONS).values_list('kind').annotate(n=Count('id'))))
    return {
        'days': days,
        'periods': PERIODS,
        'include_datacenters': include_datacenters,
        'kpis': {
            'visits': views.count(),
            'visitors': views.exclude(visitor_id='').values('visitor_id').distinct().count(),
            'returning': returning,
            'organizations': len(organizations),
            'private_visitors': private_visitors,
            'private_visits': private_visits,
            'cv_downloads': conversions[Event.Kind.CV_DOWNLOAD],
            'contacts': conversions[Event.Kind.CONTACT_SUBMIT],
            'newsletter': conversions[Event.Kind.NEWSLETTER],
            'avg_reading': int(reading),
        },
        'organizations': organizations[:50],
        'channels': sorted(channel_rows.values(), key=lambda r: -r['visits']),
        'sources': sources,
        'referrers': referrers,
        'campaigns': campaigns,
        'pages': pages,
        'cases': cases,
        'outbound': outbound,
        'returning_visitors': returning_rows[:25],
        'chart': chart,
        'activity': activity,
    }


def organization_detail(key: str, days: int) -> dict | None:
    """Timeline of one network: its sessions with pages read and events, newest first."""
    since = timezone.now() - timedelta(days=days)
    if key.startswith('as') and key[2:].isdigit():
        match = Q(asn=int(key[2:]))
    elif key.startswith('name:'):
        match = Q(asn__isnull=True, organization=key[5:])
    else:
        return None
    views = list(PageView.objects.filter(match, timestamp__gte=since).select_related('channel').order_by('-timestamp'))
    if not views:
        return None
    events = list(Event.objects.filter(match, timestamp__gte=since).order_by('-timestamp'))
    labels = _labels()
    name, kind = _name(views[0].asn, views[0].organization, views[0].network_type, labels)

    sessions = defaultdict(lambda: {'pages': [], 'events': []})
    for pv in views:
        s = sessions[pv.session_id]
        s['pages'].append(pv)
        s.setdefault('visitor', pv.visitor_id[:6])
        s['start'] = pv.timestamp
        s.setdefault('end', pv.timestamp)
        s.setdefault('channel', pv.channel.name if pv.channel else '')
        s.setdefault('source', pv.get_source_display())
        s.setdefault('device', pv.get_device_display())
        s.setdefault('country', pv.country)
    for ev in events:
        if ev.session_id in sessions:
            sessions[ev.session_id]['events'].append({'kind': ev.get_kind_display(), 'label': ev.label,
                                                      'icon': EVENT_ICONS.get(ev.kind, 'bi-dot'), 'when': ev.timestamp})
    timeline = sorted(sessions.values(), key=lambda s: s['start'], reverse=True)
    for s in timeline:
        s['pages'].sort(key=lambda pv: pv.timestamp)
        s['reading'] = sum(pv.time_spent for pv in s['pages'])

    return {
        'key': key,
        'asn': views[0].asn,
        'name': name,
        'type_label': NetworkType(kind).label,
        'visits': len(views),
        'visitors': len({pv.visitor_id for pv in views}),
        'days_active': len({pv.timestamp.date() for pv in views}),
        'conversions': sum(1 for ev in events if ev.kind in Event.CONVERSIONS),
        'timeline': timeline,
        'days': days,
        'has_label': views[0].asn in labels,
    }
