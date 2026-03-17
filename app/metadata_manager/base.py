from rest_framework.decorators import action
from rest_framework.response import Response
from .views import GenericMetadataViewSet

class MetadataManager:
    """
    Base class for configuring a Metadata-Driven component.
    """
    model = None
    fields_to_display = []
    editable_fields = []
    mode = 'edit'  # 'read_only' | 'edit'
    inline_editing = True
    enable_export = True
    enable_reorder = True
    pagination_size = 20
    enable_quick_filter = True

    @classmethod
    def get_viewset(cls):
        """
        Returns a ViewSet configured with this metadata.
        """
        class ConfiguredViewSet(GenericMetadataViewSet):
            model = cls.model
            fields_to_display = cls.fields_to_display
            editable_fields = cls.editable_fields if cls.mode == 'edit' else []
            pagination_size = cls.pagination_size
            
            # Additional attributes to pass to frontend
            extra_config = {
                'mode': cls.mode,
                'inline_editing': cls.inline_editing,
                'enable_export': cls.enable_export,
                'enable_reorder': cls.enable_reorder,
                'enable_quick_filter': cls.enable_quick_filter,
            }

            @action(detail=False, methods=['get'], url_path='metadata_config')
            def metadata_config(self, request):
                config = super().metadata_config(request).data
                config.update(self.extra_config)
                return Response(config)

        return ConfiguredViewSet
