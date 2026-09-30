"""Where a visit comes from: own channel (?src=), UTM campaign, social network, search engine..."""
from urllib.parse import parse_qs, urlsplit

from .models import TrafficSource

SEARCH = ('google.', 'bing.', 'duckduckgo.', 'yahoo.', 'ecosia.', 'qwant.', 'yandex.', 'baidu.', 'startpage.',
          'search.brave.', 'perplexity.', 'chatgpt.', 'chat.openai.', 'claude.ai', 'copilot.microsoft.')
SOCIAL = ('linkedin.', 'lnkd.in', 't.co', 'twitter.', 'x.com', 'facebook.', 'fb.', 'instagram.', 'youtube.',
          'reddit.', 'github.', 'medium.', 'dev.to', 'news.ycombinator.', 'slack.', 'telegram.', 'whatsapp.',
          'mastodon.', 'threads.', 'bsky.')
WEBMAIL = ('mail.google.', 'outlook.', 'office.com', 'office365.', 'mail.yahoo.', 'mail.proton.', 'webmail.')


def referrer_domain(referrer: str) -> str:
    host = (urlsplit(referrer).hostname or '').lower()
    return host[4:] if host.startswith('www.') else host


def _matches(host: str, patterns: tuple[str, ...]) -> bool:
    return any(host == p.rstrip('.') or host.startswith(p) or f'.{p}' in f'.{host}' for p in patterns)


def classify_source(query_string: str, referrer: str, own_host: str, has_channel: bool) -> dict:
    """Return source, referrer_domain and the utm_* values for one page view."""
    params = parse_qs(query_string)
    utm = {k: (params.get(k, [''])[0] or '')[:100] for k in ('utm_source', 'utm_medium', 'utm_campaign')}
    host = referrer_domain(referrer)

    if has_channel:
        source = TrafficSource.CHANNEL
    elif utm['utm_source'] or utm['utm_campaign']:
        source = TrafficSource.CAMPAIGN
    elif not host:
        source = TrafficSource.DIRECT
    elif host == own_host or host.endswith('.' + own_host):
        source = TrafficSource.INTERNAL
    elif _matches(host, WEBMAIL):
        source = TrafficSource.EMAIL
    elif _matches(host, SOCIAL):
        source = TrafficSource.SOCIAL
    elif _matches(host, SEARCH):
        source = TrafficSource.SEARCH
    else:
        source = TrafficSource.REFERRAL
    return {'source': source, 'referrer_domain': host[:150], **utm}
