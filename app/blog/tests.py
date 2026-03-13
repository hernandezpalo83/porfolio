from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.blog.models import Category, Post


class BlogViewsTest(TestCase):
	def setUp(self):
		self.User = get_user_model()
		self.user = self.User.objects.create_user(username='testuser', password='pass')
		self.category = Category.objects.create(name='Test', slug='test')

	def test_post_list_empty(self):
		url = reverse('blog:post_list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)

	def test_post_list_with_posts(self):
		Post.objects.create(
			title='Hello',
			slug='hello',
			author=self.user,
			category=self.category,
			content='Content',
			status='published',
		)
		url = reverse('blog:post_list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Hello')

	def test_post_detail(self):
		post = Post.objects.create(
			title='Detail',
			slug='detail',
			author=self.user,
			category=self.category,
			content='Content',
			status='published',
		)
		url = reverse('blog:post_detail', args=[post.slug])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, post.title)
