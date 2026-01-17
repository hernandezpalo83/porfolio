from django.urls import path
from .views import prompt_library
from . import views

app_name = 'prompts'

urlpatterns = [
    # ... tus otras urls ...
    path('', prompt_library, name='prompt_library'),
    path('delete/<int:index>/', views.delete_prompt, name='delete_prompt'),
]