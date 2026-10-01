"""
Who owns the network a visit comes from (the "company" behind it), resolved offline.

Uses the DB-IP ASN Lite database (CC BY 4.0, https://db-ip.com), downloaded on
every deploy by `manage.py update_network_db`. The IP address is only used in
memory for the lookup: it is never stored nor sent to a third party.

Classification, from most to least reliable:
1. NetworkLabel rows edited in the admin (e.g. "AS12345 = Indra, empresa").
2. Keyword rules below: operators, mobile carriers, clouds, corporate proxies...
3. Anything else with an owner name is treated as a business network.
"""
import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import NetworkLabel, NetworkType

logger = logging.getLogger(__name__)

# Order matters: the first matching rule wins
RULES: list[tuple[str, str]] = [
    # Corporate security proxies: the visitor is at a company, but we cannot know which one
    (NetworkType.CORPORATE_PROXY, r'zscaler|netskope|forcepoint|palo alto|prisma access|cato networks|'
                                  r'iboss|menlo security|skyhigh|mcafee|symantec|broadcom|cloudflare warp'),
    (NetworkType.HOSTING, r'amazon|aws|google cloud|google llc|microsoft azure|digitalocean|ovh|hetzner|'
                          r'linode|akamai|vultr|oracle cloud|alibaba|tencent|contabo|scaleway|ionos|'
                          r'hostinger|leaseweb|choopa|m247|datacamp|cdn77|fastly|cloudflare|render|'
                          r'heroku|github|facebook|meta platforms|apple inc|hosting|datacenter|data center|'
                          r'server|vps|colocation|cloud'),
    (NetworkType.MOBILE, r'mobile|movil|móvil|wireless|cellular|\blte\b|\b5g\b|t-mobile|simyo|lowi|pepephone|'
                         r'\bo2\b|yoigo'),
    # Internet backbones / transit carriers and big foreign ISPs: never the company that visits
    (NetworkType.ISP, r'level 3|lumen|centurylink|cogent|zayo|hurricane electric|\bgtt\b|\bntt\b|telia|'
                      r'arelion|tata comm|pccw|\brcn\b|frontier|windstream|optimum|altice|mediacom|'
                      r'suddenlink|\bwow\b|shaw|rogers|bell canada|telus|reliance jio|airtel|'
                      r'\bcommunications?\b|\bcommunication services\b'),
    (NetworkType.ISP, r'telefonica|telefónica|movistar|vodafone|orange|jazztel|masmovil|másmóvil|xfera|'
                      r'\bdigi\b|avatel|adamo|euskaltel|telecable|r cable|parlem|finetwork|'
                      r'lyntia|aire networks|comcast|verizon|at&t|charter|cox comm|spectrum|\bbt\b|'
                      r'deutsche telekom|telekom|telecom italia|\btim\b|free sas|\bsfr\b|bouygues|proximus|'
                      r'telenet|kpn|ziggo|swisscom|\bsky\b|virgin media|liberty global|nos comunica|\bmeo\b|'
                      r'telmex|claro|telecom argentina|broadband|telecom|telecommunications|internet service|'
                      r'cable|fibra|fiber|fibre|\bisp\b|net s\.?l|comunicaciones|telecomunicaciones'),
    (NetworkType.EDUCATION, r'universi|rediris|educa|college|school|academ|csic|consorci de serveis universitaris'),
    (NetworkType.GOVERNMENT, r'ministerio|gobierno|government|ayuntamiento|generalitat|junta de|diputaci|'
                             r'comunidad de madrid|administraci|red sara|red\.es|policia|ejercito|defensa'),
]
_COMPILED = [(kind, re.compile(pattern, re.IGNORECASE)) for kind, pattern in RULES]
_LEGAL_SUFFIX = re.compile(r'[,.]?\s+(s\.?a\.?u?\.?|s\.?l\.?u?\.?|inc\.?|llc|ltd\.?|gmbh|b\.?v\.?|plc|corp\.?|'
                           r'corporation|limited|ag|s\.?p\.?a\.?|sas)$', re.IGNORECASE)


_STOPWORDS = {'de', 'del', 'la', 'las', 'los', 'el', 'y', 'e', 'of', 'the', 'and', 'für', 'du', 'des'}


@dataclass(frozen=True)
class NetworkInfo:
    asn: int | None
    organization: str
    network_type: str


UNKNOWN = NetworkInfo(asn=None, organization='', network_type=NetworkType.UNKNOWN)


def database_path() -> Path:
    return Path(getattr(settings, 'NETWORK_DB_PATH', Path(settings.BASE_DIR) / 'data' / 'dbip-asn-lite.mmdb'))


@lru_cache(maxsize=1)
def _reader():
    path = database_path()
    if not path.exists():
        logger.warning("Network database missing at %s: run manage.py update_network_db", path)
        return None
    import maxminddb
    return maxminddb.open_database(str(path))


def reload_database() -> None:
    _reader.cache_clear()


def classify(organization: str) -> str:
    for kind, pattern in _COMPILED:
        if pattern.search(organization):
            return kind
    return NetworkType.BUSINESS if organization else NetworkType.UNKNOWN


def tidy_name(organization: str) -> str:
    """'TELEFONICA DE ESPANA S.A.U.' → 'Telefonica De Espana'; keeps short acronyms (BBVA, IBM)."""
    name = _LEGAL_SUFFIX.sub('', organization.strip()).strip(' ,.')
    if name.isupper():
        name = ' '.join(
            w.lower() if w.lower() in _STOPWORDS else (w if len(w) <= 4 else w.capitalize())
            for w in name.split()
        )
    return name[:150]


def _label(asn: int) -> NetworkLabel | None:
    key = f'analytics:network-label:{asn}'
    label = cache.get(key)
    if label is None:
        label = NetworkLabel.objects.filter(asn=asn).first() or False
        cache.set(key, label, 60 * 10)
    return label or None


def lookup(ip: str) -> NetworkInfo:
    reader = _reader()
    if not ip or reader is None:
        return UNKNOWN
    try:
        record = reader.get(ip) or {}
    except ValueError:
        return UNKNOWN
    asn = record.get('autonomous_system_number')
    owner = record.get('autonomous_system_organization') or ''
    if asn:
        label = _label(asn)
        if label:
            return NetworkInfo(asn=asn, organization=label.name, network_type=label.network_type)
    return NetworkInfo(asn=asn, organization=tidy_name(owner), network_type=classify(owner))


@receiver(post_save, sender=NetworkLabel)
@receiver(post_delete, sender=NetworkLabel)
def _forget_label(sender, instance, **kwargs):
    cache.delete(f'analytics:network-label:{instance.asn}')
