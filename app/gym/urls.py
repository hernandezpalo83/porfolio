from django.urls import path, include
from .views import ProductHTMxTableView, lista_productos, mantenimiento_productos
from rest_framework.routers import DefaultRouter
from .api import ProductoViewSet

router = DefaultRouter()
router.register(r'productos-api', ProductoViewSet, basename='producto-api')

app_name = 'gym'

urlpatterns = [
    path('productos/', lista_productos, name='lista_productos'),
    path('products/', ProductHTMxTableView.as_view(), name='product_list'),
    path('mantenimiento/', mantenimiento_productos, name='mantenimiento_productos'),
    path('api/', include(router.urls)),
]