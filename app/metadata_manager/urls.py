from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.gym.models import Producto
from .base import Lista
from django.shortcuts import render

# 1. Definición de la Configuración de Metadatos
class ProductoMetadata(Lista):
    model = Producto
    titulo = 'Productos'
    descripcion = 'Administración de productos'
    fields_to_display = ['nombre', 'descripcion', 'precio', 'stock']
    editable_fields = ['nombre', 'descripcion', 'precio', 'stock']
    mode = 'edit'
    inline_editing = False
    pagination_size = 10

# 2. Configuración del Router de la API
router = DefaultRouter()
router.register(r'productos', ProductoMetadata.get_viewset(), basename='producto-metadata')

# 3. Vista Genérica para el Renderizado del HTML
def generic_metadata_view(request, metadata_class, config_url, api_url):
    """
    Renderiza la tabla mantenimiento.html con la configuración de AG Grid.
    """
    return render(request, 'private/pages/metadata_manager/mantenimiento.html', {
        'titulo': getattr(metadata_class, 'titulo', 'Gestión de Datos'),
        'descripcion': getattr(metadata_class, 'descripcion', 'Administración de registros.'),
        'config_url': config_url,
        'api_url': api_url,
    })

# 4. Vistas de acceso (Wrappers para evitar usar Lambdas)
def productos_gestion_view(request):
    return generic_metadata_view(
        request, 
        ProductoMetadata, 
        '/mantenimiento/productos/metadata_config/', 
        '/mantenimiento/productos/'
    )

# 5. URLs: EL ORDEN ES CRÍTICO AQUÍ
app_name = 'mantenimiento'

urlpatterns = [
    # PRIMERO: La ruta específica para el HTML
    path('productos/gestion/', productos_gestion_view, name='productos_gestion'),

    # SEGUNDO: Las rutas automáticas del router para la API (JSON)
    path('', include(router.urls)),
]