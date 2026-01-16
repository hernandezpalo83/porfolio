from django.urls import path
from . import views
from django.conf import settings
from django.contrib.auth.views import LogoutView


app_name = 'landing'

urlpatterns = [
    path('', views.home, name='index'),
    path('private/', views.private_area, name='private_area'),
    path('accounts/profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('private/db-backup/', views.db_backup, name='db_backup'),

]

