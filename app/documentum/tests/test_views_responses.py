from django.test import TestCase
from django.urls import reverse
from django.apps import apps


class DocumentumViewResponsesTests(TestCase):
    def setUp(self):
        Category = apps.get_model('documentum', 'Category')
        Document = apps.get_model('documentum', 'Document')
        # create category and one document
        self.cat = Category.objects.create(name='General', slug='general', is_visible=True)
        self.doc = Document.objects.create(
            title='Test Doc', slug='test-doc', category=self.cat, content_markdown='# test', status='published'
        )

    def test_category_list_returns_200(self):
        url = reverse('documentum:category_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Ensure template used is the docs/category_list.html
        self.assertTemplateUsed(resp, 'documentum/category_list.html')

    def test_document_list_returns_200(self):
        url = reverse('documentum:document_list', args=[self.cat.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'documentum/document_list.html')

    def test_document_detail_returns_200(self):
        url = reverse('documentum:document_detail', args=[self.cat.slug, self.doc.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'documentum/document_detail.html')
