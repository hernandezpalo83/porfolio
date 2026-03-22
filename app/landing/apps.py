from django.apps import AppConfig


class LandingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.landing'

    def ready(self):
        import app.landing.signals  # noqa: F401 — registra los signals de cache invalidation
