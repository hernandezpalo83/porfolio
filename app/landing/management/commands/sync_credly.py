"""Sincroniza las insignias públicas de Credly del perfil configurado en Info.credly_url."""
import logging
import re
from datetime import date

import requests
from django.core.management.base import BaseCommand

from app.landing.models import CredlyBadge, Info

logger = logging.getLogger(__name__)

USER_RE = re.compile(r'credly\.com/users/([^/?#]+)')
API = 'https://www.credly.com/users/{user}/badges.json'
TIMEOUT = 10
MAX_PAGES = 10


def _date(value):
    return date.fromisoformat(value) if value else None


def fetch_badges(user: str) -> list[dict]:
    """All public badges of a Credly user (the endpoint is paginated)."""
    badges, page = [], 1
    while page and page <= MAX_PAGES:
        resp = requests.get(API.format(user=user), params={'page': page}, timeout=TIMEOUT,
                            headers={'Accept': 'application/json', 'User-Agent': 'hernandezpalo.es sync'})
        resp.raise_for_status()
        data = resp.json()
        badges.extend(data.get('data', []))
        meta = data.get('metadata') or {}
        page = page + 1 if meta.get('next_page_url') else None
    return badges


class Command(BaseCommand):
    help = "Importa o actualiza las insignias públicas de Credly (Info.credly_url)."

    def handle(self, *args, **options):
        info = Info.objects.exclude(credly_url='').first()
        match = USER_RE.search(info.credly_url) if info else None
        if not match:
            self.stdout.write("Sin perfil de Credly configurado en Info: nada que sincronizar.")
            return

        try:
            remote = fetch_badges(match.group(1))
        except (requests.RequestException, ValueError) as exc:
            # Non-critical: the section keeps the last synced badges and the profile link
            self.stdout.write(self.style.WARNING(f"No se pudo leer Credly: {exc}"))
            return

        seen = set()
        for item in remote:
            template = item.get('badge_template') or {}
            entities = (item.get('issuer') or {}).get('entities') or []
            seen.add(item['id'])
            CredlyBadge.objects.update_or_create(
                credly_id=item['id'],
                defaults={
                    'name': template.get('name', '')[:200],
                    'issuer': (entities[0]['entity']['name'] if entities else '')[:150],
                    'image_url': item.get('image_url') or template.get('image_url', ''),
                    'badge_url': f"https://www.credly.com/badges/{item['id']}",
                    'issued_at': _date(item.get('issued_at_date')) or date.today(),
                    'expires_at': _date(item.get('expires_at_date')),
                },
            )
        removed, _ = CredlyBadge.objects.exclude(credly_id__in=seen).delete()
        self.stdout.write(self.style.SUCCESS(
            f"Credly sincronizado: {len(seen)} insignias, {removed} eliminadas."
        ))
