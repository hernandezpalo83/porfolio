from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'app.blog'

    def ready(self):
        import app.blog.signals  # noqa: F401
