from django.urls import path
from . import views
from django.conf import settings
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.home, name='home'),
    path('private/', views.private_area, name='private'),
    path('accounts/profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),

]