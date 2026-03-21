from django.urls import path, include
from .views import mantenimiento_productos
from rest_framework.routers import DefaultRouter
from .api import ProductoViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='productos')

app_name = 'gym'

urlpatterns = [
    path('mantenimiento/', mantenimiento_productos, name='mantenimiento_productos'),
    path('api/', include(router.urls)),
]