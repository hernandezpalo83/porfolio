from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Producto
from .serializers import ProductoSerializer

class MetadataMixin:
    @action(detail=False, methods=['get'])
    def metadata(self, request):
        """Returns field metadata for the model."""
        serializer = self.get_serializer()
        fields = serializer.fields
        metadata = []
        
        # Mapping DRF fields to simple types for JS
        type_mapping = {
            'CharField': 'text',
            'TextField': 'textarea',
            'DecimalField': 'number',
            'IntegerField': 'number',
            'PositiveIntegerField': 'number',
            'DateTimeField': 'datetime',
            'DateField': 'date',
            'BooleanField': 'boolean',
        }
        
        for name, field in fields.items():
            if name == 'id': continue
            
            f_type = field.__class__.__name__
            metadata.append({
                'name': name,
                'label': field.label or name.capitalize(),
                'type': type_mapping.get(f_type, 'text'),
                'required': field.required,
                'read_only': field.read_only,
                'help_text': field.help_text,
            })
            
        return Response(metadata)

class ProductoViewSet(MetadataMixin, viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('-fecha_creacion')
    serializer_class = ProductoSerializer
