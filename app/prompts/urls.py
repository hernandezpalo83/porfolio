from django.urls import path
from .views import prompt_library

app_name = 'prompts'

urlpatterns = [
    # ... tus otras urls ...
    path('', prompt_library, name='prompt_library'),
]