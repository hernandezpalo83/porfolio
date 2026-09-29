"""Insignias de Credly: sincronización y franja en Formación."""
from unittest import mock

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from app.landing.models import CredlyBadge, Info

PROFILE = 'https://www.credly.com/users/javier-hernandez.53ccb137/badges'


def credly_page(*badges):
    return {'data': list(badges), 'metadata': {'next_page_url': None}}


def badge(uid, name, issuer='Cisco', issued='2024-01-10'):
    return {
        'id': uid, 'issued_at_date': issued, 'expires_at_date': None,
        'image_url': f'https://images.credly.com/images/{uid}/blob',
        'badge_template': {'name': name},
        'issuer': {'entities': [{'entity': {'name': issuer}}]},
    }


class SyncCredlyTests(TestCase):
    fixtures = ['test_landing.json']

    def setUp(self):
        Info.objects.update(credly_url=PROFILE)

    def run_sync(self, payload):
        response = mock.Mock(status_code=200)
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        with mock.patch('app.landing.management.commands.sync_credly.requests.get', return_value=response) as get:
            call_command('sync_credly', stdout=open('/dev/null', 'w'))
        return get

    def test_imports_updates_and_keeps_hidden_flag(self):
        get = self.run_sync(credly_page(badge('a', 'Python Essentials 1'), badge('b', 'Lean', 'Certiprof')))
        self.assertIn('/users/javier-hernandez.53ccb137/badges.json', get.call_args.args[0])
        self.assertEqual(CredlyBadge.objects.count(), 2)
        CredlyBadge.objects.filter(credly_id='b').update(is_visible=False)

        self.run_sync(credly_page(badge('a', 'Python Essentials 1 (2023)'), badge('b', 'Lean', 'Certiprof')))
        self.assertEqual(CredlyBadge.objects.get(credly_id='a').name, 'Python Essentials 1 (2023)')
        self.assertFalse(CredlyBadge.objects.get(credly_id='b').is_visible)

    def test_removes_badges_no_longer_public(self):
        self.run_sync(credly_page(badge('a', 'A'), badge('b', 'B')))
        self.run_sync(credly_page(badge('a', 'A')))
        self.assertEqual(list(CredlyBadge.objects.values_list('credly_id', flat=True)), ['a'])

    def test_network_error_keeps_existing_badges(self):
        import requests
        self.run_sync(credly_page(badge('a', 'A')))
        with mock.patch('app.landing.management.commands.sync_credly.requests.get',
                        side_effect=requests.ConnectionError('down')):
            call_command('sync_credly', stdout=open('/dev/null', 'w'))
        self.assertTrue(CredlyBadge.objects.filter(credly_id='a').exists())


class CredlyBandTests(TestCase):
    fixtures = ['test_landing.json']

    def setUp(self):
        cache.clear()
        Info.objects.update(credly_url=PROFILE)
        for i in range(7):
            CredlyBadge.objects.create(credly_id=str(i), name=f'Insignia {i}', issuer='Cisco',
                                       image_url=f'https://images.credly.com/{i}.png',
                                       badge_url=f'https://www.credly.com/badges/{i}',
                                       issued_at=f'2024-01-0{i + 1}')
        CredlyBadge.objects.filter(credly_id='6').update(is_visible=False)

    def test_band_shows_count_latest_badges_and_profile_link(self):
        resp = self.client.get(reverse('landing:index'))
        self.assertContains(resp, '<strong>6</strong> insignias verificadas', html=False)
        self.assertContains(resp, f'href="{PROFILE}"')
        self.assertContains(resp, 'Insignia 5')           # newest visible
        self.assertNotContains(resp, 'Insignia 6')        # hidden from the admin
        self.assertContains(resp, '>+1</li>', html=False)  # 6 visible, 5 shown
        self.assertIn('images.credly.com', resp['Content-Security-Policy'])
        self.assertContains(resp, PROFILE)                 # JSON-LD sameAs

    def test_no_profile_no_band(self):
        Info.objects.update(credly_url='')
        self.assertNotContains(self.client.get(reverse('landing:index')), 'aria-labelledby="credly-title"')
