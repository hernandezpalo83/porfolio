from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # hernandezpalo.es/blog/
    path('', views.post_list, name='post_list'),
    
    # hernandezpalo.es/blog/categoria/nombre-del-post/
    path('<slug:post>/', views.post_detail, name='post_detail'),
    
    # hernandezpalo.es/blog/category/gestion-de-producto/
    path('category/<slug:category_slug>/', views.post_list, name='post_list_by_category'),
]