from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.http import HttpResponse # Importante añadir esto

from django.contrib.sitemaps.views import sitemap
from app.landing.sitemaps import StaticViewSitemap
from app.blog.sitemaps import PostSitemap
from django.conf import settings
from django.conf.urls.static import static
from app.documentum.sitemaps import DocumentSitemap, CategorySitemap

from django.views.generic import TemplateView

sitemaps = {
    'static': StaticViewSitemap,
    'blog': PostSitemap,
    'docs_docs': DocumentSitemap,
    'docs_cats': CategorySitemap,
}

urlpatterns = [
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='landing/pages/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        
    path('blog/', include('app.blog.urls', namespace='blog')),

    path('gym/', include('app.gym.urls')),
    path('prompts/', include('app.prompts.urls')),
    path('docs/', include('app.documentum.urls', namespace='docs')),

    path('', include('app.landing.urls')),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)