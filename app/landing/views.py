from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from app.utils.content_cache import cached
from django.core.management import call_command
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django_ratelimit.decorators import ratelimit
from .models import Info, Skill, Experience, Education, Project, Metric, CompanyCollaboration, CredlyBadge
from app.blog.models import Post
from .forms import FormularioContacto
from .seo import home_structured_data
from .portfolio import build_portfolio
from django.contrib import messages
import logging
from typing import Dict, Any

import io

logger = logging.getLogger(__name__)

def error_404_view(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, 'landing/pages/404.html', status=404)

@login_required
def private_area(request: HttpRequest) -> HttpResponse:
    # Mostrar diagnóstico si el usuario es superuser
    diagnostics = None
    if request.user.is_superuser:
        try:
            import json
            from django.urls import reverse
            # Crear request interno para obtener diagnóstico
            from django.test import RequestFactory
            factory = RequestFactory()
            diag_request = factory.get(reverse('debug_diagnostics'))
            diag_request.user = request.user

            # Llamar a la función debug_diagnostics directamente
            from app.config.urls import debug_diagnostics
            response = debug_diagnostics(diag_request)
            diagnostics = json.loads(response.content.decode())
        except Exception as e:
            logger.error(f"Error loading diagnostics: {e}")
            diagnostics = None

    context: Dict[str, Any] = {
        'segment': 'dashboard',
        'diagnostics': diagnostics,
    }
    return render(request, 'private/pages/dashboard.html', context)

@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """
    Perfil de usuario en zona privada.
    Redirigimos a private_area que es la dashboard principal.
    """
    return redirect('landing:private_area')

def _build_home_data() -> Dict[str, Any]:
    home_data: Dict[str, Any] = {
        'info': Info.objects.first(),
        'skills': list(Skill.objects.all().order_by('-score')),
        'experiences': list(Experience.objects.prefetch_related('technologies').order_by('-start_date')),
        'education': list(Education.objects.all().order_by('-start_date')),
        # get_read_time needs 'content': deferring it cost one extra query per post on every request
        'latest_posts': list(
            Post.objects.filter(status='published')
            .only('title', 'slug', 'excerpt', 'content', 'publish', 'imagen_url', 'category_id', 'author_id')
            .order_by('-publish')[:3]
        ),
        'metrics': list(Metric.objects.filter(is_visible=True).order_by('order')),
        'companies': list(CompanyCollaboration.objects.filter(is_active=True).order_by('order')),
        'credly_badges': list(CredlyBadge.objects.filter(is_visible=True)[:5]),
        'credly_count': CredlyBadge.objects.filter(is_visible=True).count(),
        'credly_issuers': list(CredlyBadge.objects.filter(is_visible=True).exclude(issuer='')
                               .values_list('issuer', flat=True).distinct().order_by('issuer')),
    }
    home_data['projects'], home_data['project_filters'] = build_portfolio(Project.objects.all())
    return home_data


@ratelimit(key='ip', rate='5/h', method='POST', block=False)
def home(request: HttpRequest) -> HttpResponse:
    # 1. GESTIÓN DEL FORMULARIO (POST)
    if request.method == 'POST':
        if getattr(request, 'limited', False):
            messages.error(request, 'Demasiados intentos. Por favor, espera un momento antes de volver a enviar.')
            return redirect('/#contact')
        form = FormularioContacto(request.POST)
        if form.is_valid():
            # Guardamos en la base de datos (Modelo Contacto)
            form.save()
            # Mensaje de éxito para el usuario
            messages.success(request, '📩 ¡Tu mensaje está en camino! Te responderé lo antes posible.')
            # Redirigimos al ancla de contacto para limpiar los campos y mostrar el mensaje
            return redirect('/#contact')
        else:
            # Si el formulario no es válido (ej. fallo de reCAPTCHA),
            # registramos los errores para debugging
            logger.warning(f"Form validation failed: {form.errors}")
            messages.error(request, 'Hubo un problema con el envío. Por favor, revisa los campos y el captcha.')
    else:
        # Carga inicial de la página
        form = FormularioContacto()

    # 2. CARGA DE DATOS PARA LA LANDING (GET): caché versionada, se invalida al guardar
    #    cualquier modelo de la landing o del blog (últimos artículos)
    home_data = cached(('landing', 'blog'), 'home', _build_home_data, ttl=60 * 30)
    context: Dict[str, Any] = {
        **home_data,
        'form': form,
        'structured_data': home_structured_data(home_data),
    }
    return render(request, 'landing/pages/home.html', context)

def privacy(request: HttpRequest) -> HttpResponse:
    """Aviso legal, política de privacidad y cookies (RGPD / LSSI-CE)."""
    return render(request, 'landing/pages/privacy.html', {'info': Info.objects.first()})


def is_superuser(user) -> bool:
    return user.is_authenticated and user.is_superuser
    
@user_passes_test(is_superuser)
def export_data_view(request: HttpRequest) -> HttpResponse:
    """
    Exporta los datos de las apps landing y gym a un JSON descargable.
    Solo accesible por superusuarios.
    """
    logger.info(
        "Backup export initiated",
        extra={'user': getattr(request.user, 'username', 'unknown'),
               'ip': request.META.get('REMOTE_ADDR', '?')}
    )
    buffer = io.StringIO()

    call_command(
        "dumpdata",
        "landing",
        "gym",
        indent=2,
        stdout=buffer,
    )

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/json"
    )
    response["Content-Disposition"] = 'attachment; filename="db_backup.json"'

    return response

@login_required
@user_passes_test(lambda u: u.is_superuser) # Seguridad: solo superusuarios
def db_backup(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    if request.method == 'POST':
        if request.POST.get('action') == 'export':
            return export_data_view(request)

    # Si alguien intenta entrar por GET, lo mandamos de vuelta
    return redirect('landing:private_area')