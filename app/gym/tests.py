"""
Tests para app.gym: modelos, API y vistas.
Cobertura objetivo: >90%
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_producto(**kwargs):
    from app.gym.models import Producto
    defaults = dict(
        nombre="Producto Test",
        descripcion="Descripción de prueba",
        precio=Decimal("10.00"),
        coste=Decimal("5.00"),
        stock=100,
        estado=Producto.Estado.ACTIVE,
    )
    defaults.update(kwargs)
    return Producto.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class ProductoModelTests(TestCase):

    def test_str_representation(self):
        p = make_producto(nombre="Proteína", precio=Decimal("29.99"))
        self.assertIn("Proteína", str(p))
        self.assertIn("29.99", str(p))

    def test_default_estado_is_active(self):
        from app.gym.models import Producto
        p = make_producto()
        self.assertEqual(p.estado, Producto.Estado.ACTIVE)

    def test_ordering_by_nombre(self):
        from app.gym.models import Producto
        make_producto(nombre="Z-producto")
        make_producto(nombre="A-producto")
        nombres = list(Producto.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))

    def test_clean_precio_menor_coste_raises(self):
        from app.gym.models import Producto
        p = Producto(nombre="Test", descripcion="x", precio=Decimal("4.00"),
                     coste=Decimal("10.00"), stock=1)
        with self.assertRaises(ValidationError):
            p.clean()

    def test_clean_precio_negativo_raises(self):
        from app.gym.models import Producto
        p = Producto(nombre="Test", descripcion="x", precio=Decimal("-1.00"),
                     coste=Decimal("0.00"), stock=1)
        with self.assertRaises(ValidationError):
            p.clean()

    def test_clean_coste_negativo_raises(self):
        from app.gym.models import Producto
        p = Producto(nombre="Test", descripcion="x", precio=Decimal("10.00"),
                     coste=Decimal("-1.00"), stock=1)
        with self.assertRaises(ValidationError):
            p.clean()

    def test_clean_valid_data_passes(self):
        from app.gym.models import Producto
        p = Producto(nombre="Test", descripcion="x", precio=Decimal("10.00"),
                     coste=Decimal("5.00"), stock=10)
        try:
            p.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError on valid data")

    def test_fecha_actualizacion_updates_on_save(self):
        p = make_producto()
        original_ts = p.fecha_actualizacion
        p.nombre = "Nombre cambiado"
        p.save()
        p.refresh_from_db()
        self.assertGreaterEqual(p.fecha_actualizacion, original_ts)

    def test_fecha_creacion_immutable(self):
        p = make_producto()
        original_fecha = p.fecha_creacion
        p.nombre = "Cambiado"
        p.save()
        p.refresh_from_db()
        self.assertEqual(p.fecha_creacion, original_fecha)


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------

class ProductoAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass123')
        self.producto = make_producto()
        self.list_url = '/gym/api/productos/'
        self.detail_url = f'/gym/api/productos/{self.producto.pk}/'

    def test_list_unauthenticated_requires_auth(self):
        resp = self.client.get(self.list_url)
        # SessionAuthentication retorna 403 para anónimos (CSRF enforcement)
        self.assertIn(resp.status_code, [401, 403])

    def test_list_authenticated_returns_200(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)

    def test_list_returns_producto(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.list_url)
        data = resp.json()
        results = data.get('results', data)
        nombres = [p['nombre'] for p in results]
        self.assertIn(self.producto.nombre, nombres)

    def test_create_unauthenticated_blocked(self):
        payload = {'nombre': 'Nuevo', 'descripcion': 'x', 'precio': '15.00',
                   'coste': '5.00', 'stock': 10, 'estado': 1}
        resp = self.client.post(self.list_url, payload)
        self.assertIn(resp.status_code, [401, 403])

    def test_create_authenticated_creates_producto(self):
        self.client.force_authenticate(user=self.user)
        payload = {'nombre': 'Nuevo prod', 'descripcion': 'desc', 'precio': '15.00',
                   'coste': '5.00', 'stock': 10, 'estado': 1}
        resp = self.client.post(self.list_url, payload)
        self.assertEqual(resp.status_code, 201)
        from app.gym.models import Producto
        self.assertTrue(Producto.objects.filter(nombre='Nuevo prod').exists())

    def test_delete_unauthenticated_blocked(self):
        resp = self.client.delete(self.detail_url)
        self.assertIn(resp.status_code, [401, 403])

    def test_delete_authenticated_deletes_producto(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.delete(self.detail_url)
        self.assertEqual(resp.status_code, 204)
        from app.gym.models import Producto
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_metadata_endpoint_unauthenticated_blocked(self):
        resp = self.client.get(f'{self.list_url}metadata/')
        self.assertIn(resp.status_code, [401, 403])

    def test_metadata_endpoint_authenticated_returns_fields(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(f'{self.list_url}metadata/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        field_names = [f['name'] for f in data]
        self.assertIn('nombre', field_names)
        self.assertIn('precio', field_names)

    def test_update_precio_menor_coste_returns_400(self):
        self.client.force_authenticate(user=self.user)
        payload = {'nombre': self.producto.nombre, 'descripcion': self.producto.descripcion,
                   'precio': '1.00', 'coste': '50.00', 'stock': 1, 'estado': 1}
        resp = self.client.put(self.detail_url, payload)
        self.assertEqual(resp.status_code, 400)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class MantenimientoViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.url = reverse('gym:mantenimiento_productos')

    def test_unauthenticated_redirects_to_login(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, f'/login/?next={self.url}', fetch_redirect_response=False)

    def test_authenticated_returns_200(self):
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_context_has_required_keys(self):
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get(self.url)
        self.assertIn('titulo', resp.context)
        self.assertIn('cols', resp.context)
        self.assertIn('api_url', resp.context)

    def test_api_url_points_to_gym_api(self):
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get(self.url)
        self.assertIn('/gym/api/', resp.context['api_url'])
