from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from django.contrib.sitemaps.views import sitemap
from app.landing.sitemaps import StaticViewSitemap
from app.blog.sitemaps import PostSitemap, BlogCategorySitemap
from django.conf import settings
from django.conf.urls.static import static
from app.documentum.sitemaps import DocumentSitemap, CategorySitemap

from django.views.generic import TemplateView
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({"status": "ok"})


def csp_report(request):
    """Recibe violaciones CSP del navegador (Report-Only). Solo registra en logs."""
    import logging, json
    logger = logging.getLogger('app.config')
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            logger.warning("CSP violation: %s", body)
        except Exception:
            pass
    return JsonResponse({}, status=204)

sitemaps = {
    'static': StaticViewSitemap,
    'blog': PostSitemap,
    'blog_cats': BlogCategorySitemap,
    'wiki_docs': DocumentSitemap,
    'wiki_cats': CategorySitemap,
}

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("csp-report/", csp_report, name="csp_report"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='landing/pages/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        
    path('blog/', include('app.blog.urls', namespace='blog')),

    path('gym/', include('app.gym.urls', namespace='gym')),
    path('prompts/', include('app.prompts.urls')),
    path('wiki/', include('app.documentum.urls', namespace='wiki')),

    path('', include('app.landing.urls')),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)