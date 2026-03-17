from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.forms import modelform_factory
from django.http import JsonResponse
from .serializers import create_dynamic_serializer

class MetadataViewSetMixin:
    """
    Mixin to handle metadata configuration for the ViewSet.
    """
    model = None
    fields_to_display = []
    editable_fields = []
    pagination_size = 20

    def get_serializer_class(self):
        return create_dynamic_serializer(
            self.model, 
            self.fields_to_display, 
            self.editable_fields
        )

    def get_queryset(self):
        return self.model.objects.all()

class GenericMetadataViewSet(MetadataViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    
    @property
    def pagination_class(self):
        from rest_framework.pagination import PageNumberPagination
        class CustomPagination(PageNumberPagination):
            page_size = self.pagination_size
        return CustomPagination

    @action(detail=False, methods=['get'], url_path='metadata_config')
    def metadata_config(self, request):
        """
        Endpoint to return the configuration for AG Grid and dynamic forms.
        """
        field_info = {}
        for field_name in self.fields_to_display:
            field_info[field_name] = self._get_field_info(field_name)

        return Response({
            'model': self.model.__name__,
            'app_label': self.model._meta.app_label,
            'model_name': self.model._meta.model_name,
            'fields_to_display': self.fields_to_display,
            'editable_fields': self.editable_fields,
            'pagination_size': self.pagination_size,
            'field_info': field_info,
        })

    def _get_field_info(self, field_name):
        try:
            field = self.model._meta.get_field(field_name)
            internal_type = field.get_internal_type()
            
            field_type = 'string'
            if internal_type in ['IntegerField', 'FloatField', 'DecimalField']:
                field_type = 'number'
            elif internal_type in ['DateField', 'DateTimeField']:
                field_type = 'date'
            elif internal_type == 'BooleanField':
                field_type = 'boolean'

            return {
                'type': field_type,
                'verbose_name': str(field.verbose_name),
                'required': not field.blank,
                'editable': field_name in self.editable_fields
            }
        except:
            return {'type': 'string', 'verbose_name': field_name.capitalize(), 'required': False, 'editable': False}

def get_model_form(request, app_label, model_name, fields=None):
    """
    Endpoint to get a ModelForm for the modal editing mode.
    """
    from django.apps import apps
    model = apps.get_model(app_label, model_name)
    Form = modelform_factory(model, fields=fields or '__all__')
    # This is a simplified version; in a real scenario, you'd render the form to HTML or return a JSON schema.
    return JsonResponse({'fields': list(Form().fields.keys())})
