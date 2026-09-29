"""Caché versionada de contenido público y cabecera Server-Timing."""
import datetime

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from app.blog.models import Category as BlogCategory, Post
from app.documentum.models import Category as WikiCategory, Document
from app.landing.models import Skill


class ContentCacheTests(TestCase):
    fixtures = ['test_landing.json']

    def setUp(self):
        cache.clear()
        author = User.objects.create(username='autor')
        self.blog_cat = BlogCategory.objects.create(name='Producto', slug='producto')
        self.post = Post.objects.create(title='Primer post', slug='primer-post', author=author,
                                        category=self.blog_cat, content='<p>uno dos tres</p>',
                                        status='published', publish=datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc))
        wiki_cat = WikiCategory.objects.create(name='Guías', slug='guias', is_visible=True)
        self.doc = Document.objects.create(title='Doc', slug='doc', category=wiki_cat,
                                           content_markdown='# hola', status='published')

    def test_warm_public_pages_do_not_query_the_database(self):
        urls = [reverse('landing:index'), reverse('blog:post_list'), self.post.get_absolute_url(),
                reverse('wiki:category_list'), self.doc.category.get_absolute_url(), self.doc.get_absolute_url()]
        for url in urls:
            self.client.get(url)  # warm up
            with self.assertNumQueries(0, msg=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_saving_from_admin_refreshes_every_cached_page(self):
        self.client.get(reverse('blog:post_list'))
        self.client.get(reverse('landing:index'))
        self.post.title = 'Título nuevo'
        self.post.save()
        self.assertContains(self.client.get(reverse('blog:post_list')), 'Título nuevo')
        self.assertContains(self.client.get(reverse('landing:index')), 'Título nuevo')

        Skill.objects.create(name='Kubernetes', score=70)
        self.assertContains(self.client.get(reverse('landing:index')), 'Kubernetes')

        self.client.get(self.doc.get_absolute_url())
        self.doc.title = 'Doc renombrado'
        self.doc.save()
        self.assertContains(self.client.get(self.doc.get_absolute_url()), 'Doc renombrado')

    def test_unpublished_post_is_not_served_from_cache(self):
        self.client.get(self.post.get_absolute_url())
        self.post.status = 'draft'
        self.post.save()
        self.assertEqual(self.client.get(self.post.get_absolute_url()).status_code, 404)

    def test_search_still_queries_the_database(self):
        self.assertContains(self.client.get(reverse('blog:post_list'), {'q': 'Primer'}), 'Primer post')

    def test_server_timing_header(self):
        timing = self.client.get(reverse('landing:index'))['Server-Timing']
        for part in ('connect;dur=', 'db;dur=', 'queries', 'app;dur=', 'total;dur='):
            self.assertIn(part, timing)
