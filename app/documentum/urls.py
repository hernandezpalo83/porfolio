"""
URLs for Documentation Hub
"""

from django.urls import path
from . import views

app_name = 'docs'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('<slug:category_slug>/', views.DocumentListView.as_view(), name='document_list'),
    path('<slug:category_slug>/<slug:slug>/', views.DocumentDetailView.as_view(), name='document_detail'),
]
