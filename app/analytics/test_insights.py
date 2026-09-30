"""Analítica de reclutamiento: redes, canales, lectura, eventos y panel."""
import json
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from app.analytics.models import Channel, Event, NetworkLabel, NetworkType, PageView, SessionTracker, TrafficSource
from app.analytics.network import NetworkInfo, classify, tidy_name
from app.analytics.sources import classify_source

BROWSER = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15'
BBVA = NetworkInfo(asn=65001, organization='Banco Bilbao Vizcaya Argentaria', network_type=NetworkType.BUSINESS)
HOME = NetworkInfo(asn=3352, organization='Telefonica de Espana', network_type=NetworkType.ISP)


class NetworkClassificationTests(TestCase):
    def test_rules(self):
        self.assertEqual(classify('TELEFONICA DE ESPANA S.A.U.'), NetworkType.ISP)
        self.assertEqual(classify('Xfera Moviles S.A.'), NetworkType.MOBILE)
        self.assertEqual(classify('Zscaler Switzerland GmbH'), NetworkType.CORPORATE_PROXY)
        self.assertEqual(classify('Amazon.com, Inc.'), NetworkType.HOSTING)
        self.assertEqual(classify('Consorci de Serveis Universitaris de Catalunya'), NetworkType.EDUCATION)
        self.assertEqual(classify('INDRA SISTEMAS S.A.'), NetworkType.BUSINESS)
        self.assertEqual(tidy_name('TELEFONICA DE ESPANA S.A.U.'), 'Telefonica de Espana')

    def test_sources(self):
        self.assertEqual(classify_source('', 'https://www.linkedin.com/feed/', 'hernandezpalo.es', False)['source'],
                         TrafficSource.SOCIAL)
        self.assertEqual(classify_source('', 'https://mail.google.com/', 'hernandezpalo.es', False)['source'],
                         TrafficSource.EMAIL)
        self.assertEqual(classify_source('', 'https://www.google.es/', 'hernandezpalo.es', False)['source'],
                         TrafficSource.SEARCH)
        self.assertEqual(classify_source('', '', 'hernandezpalo.es', False)['source'], TrafficSource.DIRECT)
        utm = classify_source('utm_source=newsletter&utm_campaign=oct', '', 'hernandezpalo.es', False)
        self.assertEqual((utm['source'], utm['utm_campaign']), (TrafficSource.CAMPAIGN, 'oct'))


@override_settings(ANALYTICS_ASYNC=False, ANALYTICS_USE_CELERY=False)
class RecruiterTrackingTests(TestCase):
    fixtures = ['test_landing.json']

    def get(self, path='/', network=BBVA, **extra):
        extra.setdefault('HTTP_USER_AGENT', BROWSER)
        with mock.patch('app.analytics.middleware.lookup', return_value=network):
            return self.client.get(path, REMOTE_ADDR='198.51.100.9', **extra)

    def test_channel_and_network_are_recorded_and_inherited(self):
        self.get('/?src=linkedin')
        self.get('/blog/')
        views = list(PageView.objects.order_by('timestamp'))
        self.assertEqual([v.channel.code for v in views], ['linkedin', 'linkedin'])
        self.assertEqual({v.source for v in views}, {TrafficSource.CHANNEL})
        self.assertEqual(views[0].organization, 'Banco Bilbao Vizcaya Argentaria')
        self.assertEqual(views[0].network_type, NetworkType.BUSINESS)
        self.assertIsNone(views[0].ip_address)
        self.assertEqual(views[0].visitor_id, views[1].visitor_id)
        session = SessionTracker.objects.get()
        self.assertEqual((session.channel.code, session.page_count), ('linkedin', 2))

    def test_owner_is_never_tracked(self):
        user = User.objects.create_user('owner', password='x')
        self.client.force_login(user)
        self.get('/')
        self.assertFalse(PageView.objects.exists())

    def test_page_exposes_pageview_id_for_reading_metrics(self):
        resp = self.get('/')
        view = PageView.objects.get()
        self.assertContains(resp, f'data-pv="{view.pageview_id}"')

    def test_beacon_reading_keeps_the_maximum(self):
        self.get('/')
        view = PageView.objects.get()
        for t, s in ((40, 60), (25, 90)):
            resp = self.client.post('/a/beacon/', data=json.dumps({'type': 'read', 'pv': str(view.pageview_id), 't': t, 's': s}),
                                    content_type='text/plain', HTTP_USER_AGENT=BROWSER)
            self.assertEqual(resp.status_code, 204)
        view.refresh_from_db()
        self.assertEqual((view.time_spent, view.scroll_depth), (40, 90))

    def test_beacon_events_inherit_network_and_channel(self):
        self.get('/?src=cv')
        with mock.patch('app.analytics.middleware.lookup', return_value=BBVA):
            self.client.post('/a/beacon/', data=json.dumps({'type': 'event', 'kind': 'cv_download', 'label': 'Hero', 'path': '/'}),
                             content_type='text/plain', HTTP_USER_AGENT=BROWSER, REMOTE_ADDR='198.51.100.9')
        event = Event.objects.get()
        self.assertEqual((event.kind, event.organization, event.channel.code), ('cv_download', BBVA.organization, 'cv'))

    def test_beacon_rejects_unknown_events_and_bots(self):
        bad = self.client.post('/a/beacon/', data=json.dumps({'type': 'event', 'kind': 'hack'}),
                               content_type='text/plain', HTTP_USER_AGENT=BROWSER)
        self.assertEqual(bad.status_code, 400)
        self.client.post('/a/beacon/', data=json.dumps({'type': 'event', 'kind': 'cv_download'}),
                         content_type='text/plain', HTTP_USER_AGENT='Googlebot')
        self.assertFalse(Event.objects.exists())


@override_settings(ANALYTICS_ASYNC=False, ANALYTICS_USE_CELERY=False)
class RecruiterDashboardTests(TestCase):
    fixtures = ['test_landing.json']

    def setUp(self):
        self.admin = User.objects.create_user('admin', password='x', is_staff=True)
        linkedin = Channel.objects.get(code='linkedin')
        for day_offset, network in ((0, BBVA), (0, BBVA), (0, HOME)):
            PageView.objects.create(path='/', session_id='s-' + network.organization, visitor_id='v' + str(network.asn),
                                    asn=network.asn, organization=network.organization, network_type=network.network_type,
                                    channel=linkedin if network is BBVA else None, time_spent=120)
        Event.objects.create(kind=Event.Kind.CV_DOWNLOAD, session_id='s-x', visitor_id='v65001', asn=65001,
                             organization=BBVA.organization, network_type=NetworkType.BUSINESS, channel=linkedin)

    def test_dashboard_lists_companies_not_home_users(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('analytics:dashboard'), {'days': 30})
        self.assertEqual(resp.status_code, 200)
        orgs = resp.context['organizations']
        self.assertEqual([o.name for o in orgs], [BBVA.organization])
        self.assertEqual(orgs[0].events['cv_download'], 1)
        self.assertEqual(orgs[0].channels, ['LinkedIn'])
        self.assertEqual(resp.context['kpis']['private_visits'], 1)
        self.assertEqual(resp.context['kpis']['cv_downloads'], 1)

    def test_network_label_renames_retroactively(self):
        NetworkLabel.objects.create(asn=65001, name='BBVA', network_type=NetworkType.BUSINESS)
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(resp.context['organizations'][0].name, 'BBVA')
        detail = self.client.get(reverse('analytics:organization_detail', args=['as65001']))
        self.assertContains(detail, 'BBVA')

    def test_dashboard_requires_staff(self):
        self.client.force_login(User.objects.create_user('visitor', password='x'))
        self.assertEqual(self.client.get(reverse('analytics:dashboard')).status_code, 302)


class ReclassificationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('staff', password='x', is_staff=True)

    def test_backbones_stored_as_business_are_moved_out_and_bots_flagged(self):
        # Rows written with the first rules: Level 3 / RCN were taken for companies
        for asn, org in ((3356, 'Level 3 Communications'), (6079, 'RCN')):
            PageView.objects.create(path='/', session_id=f's{asn}', visitor_id=f'v{asn}', asn=asn,
                                    organization=org, network_type=NetworkType.BUSINESS)
        PageView.objects.create(path='/', session_id='s1', visitor_id='v1', asn=65010, organization='Acme Robots',
                                network_type=NetworkType.BUSINESS)
        PageView.objects.create(path='/', session_id='s2', visitor_id='v2', asn=65011, organization='Indra Sistemas',
                                network_type=NetworkType.BUSINESS, time_spent=45)
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('analytics:dashboard'))
        orgs = resp.context['organizations']
        self.assertEqual([o.name for o in orgs], ['Indra Sistemas', 'Acme Robots'])  # engaged first
        self.assertEqual([o.engaged for o in orgs], [True, False])
        self.assertEqual(resp.context['kpis']['organizations'], 1)
        self.assertEqual(resp.context['kpis']['organizations_no_interaction'], 1)
        self.assertContains(resp, 'Sin interacción (posible bot)')
