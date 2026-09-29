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
        url = reverse('wiki:category_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Ensure template used is the docs/category_list.html
        self.assertTemplateUsed(resp, 'documentum/category_list.html')

    def test_document_list_returns_200(self):
        url = reverse('wiki:document_list', args=[self.cat.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'documentum/document_list.html')

    def test_document_detail_returns_200(self):
        url = reverse('wiki:document_detail', args=[self.cat.slug, self.doc.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'documentum/document_detail.html')

    def test_absolute_urls_resolve(self):
        self.assertEqual(self.cat.get_absolute_url(), reverse('wiki:document_list', args=[self.cat.slug]))
        self.assertEqual(self.doc.get_absolute_url(), reverse('wiki:document_detail', args=[self.cat.slug, self.doc.slug]))

    def test_document_list_links_to_documents(self):
        resp = self.client.get(reverse('wiki:document_list', args=[self.cat.slug]))
        self.assertContains(resp, f'href="{self.doc.get_absolute_url()}"')

    def test_sitemap_includes_wiki(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.doc.get_absolute_url())


class UnpublishMigrationTests(TestCase):
    def test_vendor_and_internal_docs_become_drafts(self):
        import importlib
        from django.apps import apps as global_apps
        migration = importlib.import_module('app.documentum.migrations.0002_unpublish_vendor_and_internal_docs')
        Category = apps.get_model('documentum', 'Category')
        Document = apps.get_model('documentum', 'Document')
        vendor = Category.objects.create(name='app', slug='app', is_visible=True)
        general = Category.objects.create(name='General', slug='general', is_visible=True)
        lic = Document.objects.create(title='License.F94', slug='licensef94142512c91', category=vendor,
                                      content_markdown='MIT', status='published')
        log = Document.objects.create(title='CHANGELOG', slug='changelog', category=general,
                                      content_markdown='x', status='published')
        keep = Document.objects.create(title='Portfolio', slug='portfolio', category=general,
                                       content_markdown='x', status='published')
        migration.unpublish(global_apps, None)
        for doc in (lic, log, keep):
            doc.refresh_from_db()
        vendor.refresh_from_db()
        general.refresh_from_db()
        self.assertEqual((lic.status, log.status, keep.status), ('draft', 'draft', 'published'))
        self.assertFalse(vendor.is_visible)
        self.assertTrue(general.is_visible)
        self.assertEqual(self.client.get(lic.get_absolute_url()).status_code, 404)
