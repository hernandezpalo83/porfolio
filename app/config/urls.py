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


def debug_diagnostics(request):
    """
    ENDPOINT ÚNICO DE DIAGNÓSTICO COMPLETO.
    Requiere autenticación de superuser.
    GET /api/debug/diagnostics/

    Retorna reporte detallado de:
    - Database connection y tablas críticas
    - Module imports
    - Context processors
    - Template rendering
    """
    from django.db import connection
    from django.http import HttpResponseForbidden
    from django.template.loader import render_to_string
    import logging
    import traceback

    # Require superuser authentication
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden()

    logger = logging.getLogger(__name__)

    report = {
        'status': 'ok',
        'timestamp': str(__import__('datetime').datetime.now()),
        'sections': {
            'database': {},
            'imports': {},
            'context_processors': {},
            'templates': {}
        }
    }

    # ===== SECTION 1: DATABASE =====
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        report['sections']['database']['connection'] = {'status': '✓ OK'}
    except Exception as e:
        logger.error(f"DB Connection: {str(e)}", exc_info=True)
        report['sections']['database']['connection'] = {'status': '✗ FAIL', 'error': str(type(e).__name__)}
        report['status'] = 'error'

    # Check critical tables
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
            logger.error(f"Missing tables: {missing}")
            report['sections']['database']['tables'] = {'status': '✗ MISSING', 'missing_count': len(missing)}
            report['status'] = 'error'
        else:
            report['sections']['database']['tables'] = {'status': '✓ ALL EXIST', 'count': len(critical_tables)}
    except Exception as e:
        logger.error(f"Table check: {str(e)}", exc_info=True)
        report['sections']['database']['tables'] = {'status': '✗ FAIL', 'error': str(type(e).__name__)}
        report['status'] = 'error'

    # ===== SECTION 2: IMPORTS =====
    for module in ['app.analytics.models', 'app.analytics.middleware', 'app.landing.models', 'app.celery']:
        try:
            __import__(module)
            report['sections']['imports'][module] = '✓ OK'
        except Exception as e:
            logger.error(f"Import {module}: {str(e)}", exc_info=True)
            report['sections']['imports'][module] = f'✗ {type(e).__name__}'
            report['status'] = 'error'

    # ===== SECTION 3: CONTEXT PROCESSORS =====
    try:
        from app.landing.context_processors import menu_int_processor
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser

        factory = RequestFactory()
        req = factory.get('/')
        req.user = AnonymousUser()
        result = menu_int_processor(req)

        if 'menu_items_int' in result:
            report['sections']['context_processors']['menu_int_processor'] = '✓ OK'
        else:
            logger.error("Context processor returned invalid keys")
            report['sections']['context_processors']['menu_int_processor'] = '✗ Invalid result'
            report['status'] = 'error'
    except Exception as e:
        logger.error(f"Context processor: {str(e)}", exc_info=True)
        report['sections']['context_processors']['menu_int_processor'] = f'✗ {type(e).__name__}'
        report['status'] = 'error'

    # ===== SECTION 4: TEMPLATE RENDERING =====
    try:
        html = render_to_string('private/pages/dashboard.html', {
            'segment': 'dashboard',
            'request': request
        }, request=request)

        report['sections']['templates']['private_dashboard'] = {
            'status': '✓ OK',
            'html_length': len(html)
        }
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Template render ERROR:\n{error_trace}", exc_info=True)
        report['sections']['templates']['private_dashboard'] = {
            'status': '✗ FAIL',
            'error_type': type(e).__name__,
            'error_msg': str(e)[:300],
            'traceback_logged': True
        }
        report['status'] = 'error'

    logger.info(f"Full diagnostics: {report['status']}")
    return JsonResponse(report, status=200 if report['status'] == 'ok' else 500)


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
    path("api/debug/diagnostics/", debug_diagnostics, name="debug_diagnostics"),
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

handler404 = 'app.landing.views.error_404_view'
