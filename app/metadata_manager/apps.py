from django.apps import AppConfig

class MetadataManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.metadata_manager'
    label = 'metadata_manager'
    verbose_name = 'Metadata Manager'
