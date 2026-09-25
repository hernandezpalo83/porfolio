from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard general
    path('', views.analytics_dashboard, name='dashboard'),

    # APIs de datos (JSON)
    path('api/views-by-day/', views.api_views_by_day, name='api_views_by_day'),
    path('api/devices-distribution/', views.api_devices_distribution, name='api_devices_distribution'),
    path('api/countries-distribution/', views.api_countries_distribution, name='api_countries_distribution'),
    path('api/top-pages/', views.api_top_pages, name='api_top_pages'),
    path('api/referrers/', views.api_referrers, name='api_referrers'),

    # Blog analytics
    path('blog/', views.blog_analytics_dashboard, name='blog_dashboard'),
    path('post/<int:post_id>/', views.post_detail_analytics, name='post_detail'),
    path('api/post/<int:post_id>/views-by-day/', views.api_post_views_by_day, name='api_post_views_by_day'),
]
