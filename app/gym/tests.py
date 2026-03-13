from django.test import TestCase
from django.urls import reverse
from app.gym.models import Producto


class GymViewsTest(TestCase):
	def test_lista_productos_empty(self):
		url = reverse('gym:lista_productos')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)

	def test_lista_productos_with_items(self):
		Producto.objects.create(nombre='P1', descripcion='Desc', precio=9.99, stock=10)
		Producto.objects.create(nombre='P2', descripcion='Desc 2', precio=19.99, stock=5)
		url = reverse('gym:lista_productos')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'P1')
		self.assertContains(resp, 'P2')
