"""
Tests de vistas para app.landing.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    fixtures = ['test_landing.json']


    def test_home_returns_200(self):
        resp = self.client.get(reverse('landing:index'))
        self.assertEqual(resp.status_code, 200)

    def test_home_context_has_required_keys(self):
        resp = self.client.get(reverse('landing:index'))
        for key in ('info', 'skills', 'experiences', 'education',
                    'projects', 'latest_posts', 'metrics', 'companies', 'form'):
            self.assertIn(key, resp.context, msg=f"'{key}' missing from context")

    def test_home_query_count_bounded(self):
        # Verifica que el número de queries está acotado (no hay N+1 descontrolado)
        from django.db import connection, reset_queries
        from django.test.utils import override_settings
        with override_settings(DEBUG=True):
            reset_queries()
            self.client.get(reverse('landing:index'))
            query_count = len(connection.queries)
        self.assertLessEqual(query_count, 15, f"Demasiadas queries: {query_count}")

    def test_home_post_invalid_form_does_not_save(self):
        from app.landing.models import Contacto
        payload = {'nombre': '', 'email': 'bad', 'asunto': '', 'mensaje': ''}
        self.client.post(reverse('landing:index'), payload)
        self.assertEqual(Contacto.objects.count(), 0)


class PrivateAreaTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass1')
        self.superuser = User.objects.create_superuser(username='admin1', password='adminpass1')
        self.private_url = reverse('landing:private_area')

    def test_private_unauthenticated_redirects(self):
        resp = self.client.get(self.private_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp['Location'])

    def test_private_authenticated_returns_200(self):
        self.client.login(username='user1', password='pass1')
        resp = self.client.get(self.private_url)
        self.assertEqual(resp.status_code, 200)

    def test_db_backup_non_superuser_redirects(self):
        self.client.login(username='user1', password='pass1')
        resp = self.client.get(reverse('landing:db_backup'))
        # user_passes_test redirige si no es superuser
        self.assertIn(resp.status_code, [302, 403])

    def test_db_backup_get_redirects(self):
        self.client.login(username='admin1', password='adminpass1')
        resp = self.client.get(reverse('landing:db_backup'))
        # GET a db_backup redirige a private_area
        self.assertEqual(resp.status_code, 302)

    def test_db_backup_export_post_returns_json(self):
        self.client.login(username='admin1', password='adminpass1')
        resp = self.client.post(reverse('landing:db_backup'), {'action': 'export'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')
