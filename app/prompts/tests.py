"""
Tests para app.prompts: vistas con mock de GitHub API.
"""
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


SAMPLE_PROMPTS = [
    {"title": "Prompt A", "category": "Cat1", "description": "Desc A", "prompt": "Text A"},
    {"title": "Prompt B", "category": "Cat2", "description": "Desc B", "prompt": "Text B"},
]


class PromptLibraryAccessTests(TestCase):

    def setUp(self):
        self.url = reverse('prompts:prompt_library')
        self.superuser = User.objects.create_superuser('superadmin', password='superpass123')
        self.regular_user = User.objects.create_user('regular', password='regularpass123')

    def test_unauthenticated_redirects_to_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp['Location'])

    def test_regular_user_gets_403(self):
        self.client.login(username='regular', password='regularpass123')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_superuser_can_access(self, mock_get):
        self.client.login(username='superadmin', password='superpass123')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_superuser_sees_prompts_in_context(self, mock_get):
        self.client.login(username='superadmin', password='superpass123')
        resp = self.client.get(self.url)
        self.assertIn('prompts', resp.context)

    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_category_filter_works(self, mock_get):
        self.client.login(username='superadmin', password='superpass123')
        resp = self.client.get(self.url, {'category': 'Cat1'})
        self.assertEqual(resp.status_code, 200)


class PromptCreateTests(TestCase):

    def setUp(self):
        self.url = reverse('prompts:prompt_library')
        User.objects.create_superuser('superadmin', password='superpass123')
        self.client.login(username='superadmin', password='superpass123')

    @patch('app.prompts.views.save_to_github', return_value=True)
    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_create_valid_prompt_redirects(self, mock_get, mock_save):
        payload = {'title': 'Nuevo', 'category': 'Cat', 'description': 'Desc', 'prompt': 'Text'}
        resp = self.client.post(self.url, payload)
        self.assertRedirects(resp, self.url, fetch_redirect_response=False)

    @patch('app.prompts.views.save_to_github', return_value=True)
    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_create_without_title_does_not_save(self, mock_get, mock_save):
        payload = {'title': '', 'category': 'Cat', 'description': 'Desc', 'prompt': 'Text'}
        self.client.post(self.url, payload)
        mock_save.assert_not_called()

    @patch('app.prompts.views.save_to_github', return_value=False)
    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_github_failure_shows_error_message(self, mock_get, mock_save):
        payload = {'title': 'Test', 'category': 'Cat', 'description': 'Desc', 'prompt': 'Text'}
        resp = self.client.post(self.url, payload, follow=True)
        msgs = [str(m) for m in resp.context['messages']]
        self.assertTrue(any('error' in m.lower() or 'Error' in m for m in msgs))


class PromptEditTests(TestCase):

    def setUp(self):
        self.url = reverse('prompts:prompt_library')
        User.objects.create_superuser('superadmin', password='superpass123')
        self.client.login(username='superadmin', password='superpass123')

    @patch('app.prompts.views.save_to_github', return_value=True)
    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_edit_valid_id_calls_save(self, mock_get, mock_save):
        payload = {'id': '1', 'title': 'Editado', 'category': 'Cat', 'description': 'D', 'prompt': 'P'}
        self.client.post(self.url, payload)
        mock_save.assert_called_once()

    @patch('app.prompts.views.save_to_github', return_value=True)
    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_edit_out_of_range_id_does_not_save(self, mock_get, mock_save):
        payload = {'id': '999', 'title': 'Test', 'category': 'Cat', 'description': 'D', 'prompt': 'P'}
        self.client.post(self.url, payload)
        mock_save.assert_not_called()


class PromptDeleteTests(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser('superadmin', password='superpass123')
        self.regular_user = User.objects.create_user('regular', password='regularpass123')

    def test_delete_unauthenticated_redirects(self):
        resp = self.client.get(reverse('prompts:delete_prompt', args=[1]))
        self.assertEqual(resp.status_code, 302)

    def test_delete_regular_user_forbidden(self):
        self.client.login(username='regular', password='regularpass123')
        resp = self.client.get(reverse('prompts:delete_prompt', args=[1]))
        self.assertEqual(resp.status_code, 403)

    @patch('app.prompts.views.save_to_github', return_value=True)
    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_delete_valid_index_calls_save(self, mock_get, mock_save):
        self.client.login(username='superadmin', password='superpass123')
        self.client.get(reverse('prompts:delete_prompt', args=[1]))
        mock_save.assert_called_once()

    @patch('app.prompts.views.get_github_data', return_value=(list(SAMPLE_PROMPTS), 'sha123'))
    def test_delete_out_of_range_shows_error(self, mock_get):
        self.client.login(username='superadmin', password='superpass123')
        resp = self.client.get(reverse('prompts:delete_prompt', args=[999]), follow=True)
        msgs = [str(m) for m in resp.context['messages']]
        self.assertTrue(any('existe' in m.lower() or 'no' in m.lower() for m in msgs))
