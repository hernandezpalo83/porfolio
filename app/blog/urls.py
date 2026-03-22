from django.urls import path
from . import views
from .feeds import LatestPostsFeed, LatestPostsAtomFeed

app_name = 'blog'

urlpatterns = [
    # hernandezpalo.es/blog/
    path('', views.post_list, name='post_list'),

    # RSS / Atom feeds
    path('feed/', LatestPostsFeed(), name='post_feed_rss'),
    path('feed/atom/', LatestPostsAtomFeed(), name='post_feed_atom'),

    # Newsletter
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/confirm/<uuid:token>/', views.confirm_subscription, name='confirm_subscription'),

    # hernandezpalo.es/blog/category/gestion-de-producto/
    path('category/<slug:category_slug>/', views.post_list, name='post_list_by_category'),

    # hernandezpalo.es/blog/nombre-del-post/ (debe ir al final)
    path('<slug:post>/', views.post_detail, name='post_detail'),
]