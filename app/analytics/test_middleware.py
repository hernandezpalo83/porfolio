"""Tests del middleware de analítica: anónimo, sin latencia y solo páginas HTML de personas."""
from django.test import TestCase, override_settings

from app.analytics.models import PageView, SessionTracker

BROWSER = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Safari/604.1'


@override_settings(ANALYTICS_ASYNC=False, ANALYTICS_USE_CELERY=False)
class AnalyticsMiddlewareTests(TestCase):
    def get(self, path='/', **extra):
        extra.setdefault('HTTP_USER_AGENT', BROWSER)
        return self.client.get(path, REMOTE_ADDR='203.0.113.7', **extra)

    def test_records_anonymous_pageview(self):
        self.get('/', HTTP_CF_IPCOUNTRY='es')
        view = PageView.objects.get()
        self.assertEqual(view.country, 'ES')
        self.assertEqual(view.device, 'mobile')
        self.assertIsNone(view.ip_address)
        self.assertIsNone(view.user_agent)
        self.assertNotIn('203.0.113.7', view.session_id)

    def test_same_visitor_same_day_is_one_session(self):
        self.get('/')
        self.get('/blog/')
        session = SessionTracker.objects.get()
        self.assertEqual(session.page_count, 2)
        self.assertFalse(session.is_bounce)
        self.assertEqual(session.last_page, '/blog/')

    def test_skips_bots_non_html_and_errors(self):
        self.get('/', HTTP_USER_AGENT='Googlebot/2.1')
        self.get('/robots.txt')
        self.get('/sitemap.xml')
        self.get('/no-existe/')
        self.assertFalse(PageView.objects.exists())

    def test_unknown_country_without_cloudflare(self):
        self.get('/')
        self.assertEqual(PageView.objects.get().country, 'XX')


class RetentionTests(TestCase):
    def test_purge_keeps_recent_and_removes_old(self):
        from datetime import timedelta
        from django.core.management import call_command
        from django.utils import timezone
        from app.landing.models import Contacto
        old = PageView.objects.create(path='/', session_id='a')
        PageView.objects.filter(pk=old.pk).update(timestamp=timezone.now() - timedelta(days=91))
        PageView.objects.create(path='/', session_id='b')
        Contacto.objects.create(nombre='x', email='x@x.es', asunto='a', mensaje='m',
                                fecha_envio=timezone.now() - timedelta(days=400))
        call_command('purge_personal_data', stdout=open('/dev/null', 'w'))
        self.assertEqual(list(PageView.objects.values_list('session_id', flat=True)), ['b'])
        self.assertFalse(Contacto.objects.exists())
