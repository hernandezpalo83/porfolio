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


def debug_status(request):
    """
    Endpoint de diagnóstico PRIVADO para debuggear 500 errors.
    Requiere autenticación de superuser.
    GET /api/debug/status/
    """
    from django.db import connection
    from django.http import HttpResponseForbidden
    import logging

    # Require superuser authentication
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden()

    logger = logging.getLogger(__name__)

    status = {
        'status': 'ok',
        'checks': {}
    }

    # 1. BD connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        status['checks']['database_connection'] = '✓ OK'
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}", exc_info=True)
        status['checks']['database_connection'] = '✗ FAIL'
        status['status'] = 'error'

    # 2. Critical tables
    try:
        critical_tables = ['analytics_pageview', 'analytics_sessiontracker', 'landing_menuitem', 'auth_user']
        with connection.cursor() as cursor:
            if connection.vendor == 'sqlite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            elif connection.vendor == 'postgresql':
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            else:
                existing_tables = set()
            existing_tables = {row[0] for row in cursor.fetchall()}

        missing = [t for t in critical_tables if t not in existing_tables]
        if missing:
            logger.error(f"Missing critical tables: {missing}")
            status['checks']['critical_tables'] = f'✗ MISSING ({len(missing)})'
            status['status'] = 'error'
        else:
            status['checks']['critical_tables'] = '✓ ALL EXIST'
    except Exception as e:
        logger.error(f"Table check failed: {str(e)}", exc_info=True)
        status['checks']['critical_tables'] = '✗ FAIL'
        status['status'] = 'error'

    # 3. Critical imports
    for module in ['app.analytics.models', 'app.analytics.middleware', 'app.landing.models', 'app.celery']:
        try:
            __import__(module)
            status['checks'][f'import_{module}'] = '✓ OK'
        except Exception as e:
            logger.error(f"Import {module} failed: {str(e)}", exc_info=True)
            status['checks'][f'import_{module}'] = '✗ FAIL'
            status['status'] = 'error'

    # 4. Context processor
    try:
        from app.landing.context_processors import menu_int_processor
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser

        factory = RequestFactory()
        req = factory.get('/')
        req.user = AnonymousUser()
        result = menu_int_processor(req)

        if 'menu_items_int' in result:
            status['checks']['context_processor_menu'] = '✓ OK'
        else:
            logger.error("Context processor returned invalid result")
            status['checks']['context_processor_menu'] = '✗ FAIL'
            status['status'] = 'error'
    except Exception as e:
        logger.error(f"Context processor failed: {str(e)}", exc_info=True)
        status['checks']['context_processor_menu'] = '✗ FAIL'
        status['status'] = 'error'

    logger.info(f"Debug status check: {status['status']}")
    return JsonResponse(status, status=200 if status['status'] == 'ok' else 500)

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
    path("api/debug/status/", debug_status, name="debug_status"),
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
    path('private/analytics/', include('app.analytics.urls', namespace='analytics')),

    path('', include('app.landing.urls')),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)