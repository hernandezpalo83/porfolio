from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.gym.models import Producto
from .base import Lista
from django.shortcuts import render

# Define the Metadata configuration for Producto
class ProductoMetadata(Lista):
    model = Producto
    fields_to_display = ['nombre', 'precio', 'stock']
    editable_fields = ['nombre', 'precio', 'stock']
    mode = 'edit'
    inline_editing = True
    pagination_size = 10

router = DefaultRouter()
# Register the dynamic ViewSet
router.register(r'productos', ProductoMetadata.get_viewset(), basename='producto-metadata')

def demo_view(request):
    """
    Renders the demo page.
    """
    return render(request, 'private/pages/metadata_manager/demo.html', {
        'config_url': '/metadata/productos/metadata_config/',
        'api_url': '/metadata/productos/'
    })

urlpatterns = [
    path('', include(router.urls)),
    path('demo/', demo_view, name='metadata-demo'),
]

app_name = 'metadata'
