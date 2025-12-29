from django.urls import path
from .views import prompt_library

urlpatterns = [
    # ... tus otras urls ...
    path('prompts/', prompt_library, name='prompt_library'),
]