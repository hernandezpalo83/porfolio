from django.test import TestCase, Client, override_settings
from django.urls import reverse
from app.landing.models import Info

@override_settings(STORAGES={
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
})
class SeoTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create minimal Info object for home page rendering
        Info.objects.create(name="Javier", bio="Test bio", email="test@test.com")

    def test_robots_txt(self):
        """Test that robots.txt returns 200 and has correct content."""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        content = response.content.decode()
        self.assertIn('User-agent: *', content)
        self.assertIn('Sitemap: https://hernandezpalo.es/sitemap.xml', content)

    def test_sitemap_xml(self):
        """Test that sitemap.xml returns 200."""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        # Check XML structure basics
        self.assertIn(b'urlset', response.content)

    def test_home_seo_meta(self):
        """Test that home page has critical SEO tags."""
        response = self.client.get(reverse('landing:index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Check Canonical
        self.assertIn('<link rel="canonical"', content)
        # Check Meta Description
        self.assertIn('<meta name="description"', content)
        # Check Open Graph
        self.assertIn('property="og:title"', content)
        self.assertIn('property="og:image"', content)
        # Check Twitter Card
        self.assertIn('name="twitter:card"', content)
