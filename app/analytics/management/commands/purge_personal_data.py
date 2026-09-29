"""Apply the retention periods published in the privacy policy (/privacidad/)."""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.analytics.models import PageView, SessionTracker
from app.landing.models import Contacto

ANALYTICS_DAYS = 90
CONTACT_DAYS = 365


class Command(BaseCommand):
    help = "Borra visitas de más de 90 días y mensajes de contacto de más de 12 meses."

    def handle(self, *args, **options):
        now = timezone.now()
        views, _ = PageView.objects.filter(timestamp__lt=now - timedelta(days=ANALYTICS_DAYS)).delete()
        sessions, _ = SessionTracker.objects.filter(created_at__lt=now - timedelta(days=ANALYTICS_DAYS)).delete()
        messages, _ = Contacto.objects.filter(fecha_envio__lt=now - timedelta(days=CONTACT_DAYS)).delete()
        self.stdout.write(self.style.SUCCESS(
            f"Retención aplicada: {views} visitas, {sessions} sesiones y {messages} mensajes eliminados."
        ))
