from django.urls import path
from . import views


app_name = 'landing'

urlpatterns = [
    path('', views.home, name='index'),
    path('private/', views.private_area, name='private_area'),
    path('accounts/profile/', views.profile, name='profile'),
    path('private/db-backup/', views.db_backup, name='db_backup'),
]
