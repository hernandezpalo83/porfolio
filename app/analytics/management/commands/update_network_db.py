"""Download the monthly DB-IP ASN Lite database used to name the network of each visit."""
import gzip
import shutil
import tempfile
import time
from datetime import date
from pathlib import Path

import requests
from django.core.management.base import BaseCommand

from app.analytics.network import database_path, reload_database

URL = 'https://download.db-ip.com/free/dbip-asn-lite-{month}.mmdb.gz'
MAX_AGE_DAYS = 25


def _months_to_try(today: date) -> list[str]:
    previous = date(today.year - (today.month == 1), (today.month - 2) % 12 + 1, 1)
    return [today.strftime('%Y-%m'), previous.strftime('%Y-%m')]


class Command(BaseCommand):
    help = "Descarga la base de datos DB-IP ASN Lite (CC BY 4.0) si falta o tiene más de 25 días."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Descargar aunque sea reciente')

    def handle(self, *args, **options):
        target: Path = database_path()
        if target.exists() and not options['force']:
            age_days = (time.time() - target.stat().st_mtime) / 86400
            if age_days < MAX_AGE_DAYS:
                self.stdout.write(f"Base de datos de redes al día ({age_days:.0f} días): {target}")
                return

        target.parent.mkdir(parents=True, exist_ok=True)
        for month in _months_to_try(date.today()):
            url = URL.format(month=month)
            try:
                with requests.get(url, stream=True, timeout=60) as resp:
                    if resp.status_code != 200:
                        continue
                    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
                        with gzip.GzipFile(fileobj=resp.raw) as gz:
                            shutil.copyfileobj(gz, tmp)
                    Path(tmp.name).chmod(0o644)
                    Path(tmp.name).replace(target)
            except (requests.RequestException, OSError, EOFError) as exc:
                self.stdout.write(self.style.WARNING(f"No se pudo descargar {url}: {exc}"))
                continue
            reload_database()
            self.stdout.write(self.style.SUCCESS(f"Base de datos de redes {month} descargada en {target}"))
            return
        self.stdout.write(self.style.WARNING("No se pudo actualizar la base de datos de redes; se mantiene la anterior."))
