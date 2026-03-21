from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.blog.models import Category, Post

User = get_user_model()


def make_post(user, category, **kwargs):
    defaults = dict(
        title='Test Post', slug='test-post', author=user,
        category=category, content='Contenido de prueba', status='published',
    )
    defaults.update(kwargs)
    return Post.objects.create(**defaults)


class BlogViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.category = Category.objects.create(name='Test', slug='test')

    def test_post_list_empty(self):
        resp = self.client.get(reverse('blog:post_list'))
        self.assertEqual(resp.status_code, 200)

    def test_post_list_with_posts(self):
        make_post(self.user, self.category, title='Hello', slug='hello')
        resp = self.client.get(reverse('blog:post_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Hello')

    def test_post_list_draft_not_shown(self):
        make_post(self.user, self.category, title='Draft Post', slug='draft-post', status='draft')
        resp = self.client.get(reverse('blog:post_list'))
        self.assertNotContains(resp, 'Draft Post')

    def test_post_list_search_filter(self):
        make_post(self.user, self.category, title='Django Tips', slug='django-tips')
        make_post(self.user, self.category, title='Python Guide', slug='python-guide')
        resp = self.client.get(reverse('blog:post_list'), {'q': 'Django'})
        self.assertContains(resp, 'Django Tips')
        self.assertNotContains(resp, 'Python Guide')

    def test_post_list_pagination(self):
        for i in range(7):
            make_post(self.user, self.category, title=f'Post {i}', slug=f'post-{i}')
        resp = self.client.get(reverse('blog:post_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['posts'].has_next())

    def test_post_detail_published(self):
        post = make_post(self.user, self.category, title='Detail', slug='detail')
        resp = self.client.get(reverse('blog:post_detail', args=[post.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, post.title)

    def test_post_detail_draft_returns_404(self):
        post = make_post(self.user, self.category, title='Draft', slug='draft-d', status='draft')
        resp = self.client.get(reverse('blog:post_detail', args=[post.slug]))
        self.assertEqual(resp.status_code, 404)

    def test_post_detail_related_posts_in_context(self):
        post = make_post(self.user, self.category, title='Main', slug='main')
        make_post(self.user, self.category, title='Related', slug='related')
        resp = self.client.get(reverse('blog:post_detail', args=[post.slug]))
        self.assertIn('related_posts', resp.context)


class PostModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.category = Category.objects.create(name='Test', slug='test')

    def test_get_read_time_empty_content_returns_1(self):
        post = Post(title='T', slug='t', author=self.user, category=self.category, content='')
        self.assertEqual(post.get_read_time(), 1)

    def test_get_read_time_calculates_correctly(self):
        # 400 palabras → 2 minutos a 200 ppm
        content = 'palabra ' * 400
        post = Post(title='T', slug='t', author=self.user, category=self.category, content=content)
        self.assertEqual(post.get_read_time(), 2)

    def test_get_read_time_short_content_returns_1(self):
        post = Post(title='T', slug='t', author=self.user, category=self.category, content='Hola')
        self.assertEqual(post.get_read_time(), 1)

    def test_excerpt_auto_generated_on_save(self):
        post = make_post(self.user, self.category,
                         title='Auto Excerpt', slug='auto-exc', excerpt='')
        self.assertTrue(len(post.excerpt) > 0)

    def test_get_absolute_url(self):
        post = make_post(self.user, self.category, title='URL Test', slug='url-test')
        url = post.get_absolute_url()
        self.assertIn('url-test', url)
