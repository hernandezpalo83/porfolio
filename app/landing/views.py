from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Info, Skill, Experience, Education, Project, Contact, Metric
from app.blog.models import Post
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.contrib.auth.decorators import user_passes_test
from .forms import FormularioContacto
from django.contrib import messages
from django.shortcuts import render, redirect
import logging
from typing import Optional, Dict, Any

import io

logger = logging.getLogger(__name__)

def error_404_view(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, 'landing/pages/404.html', status=404)

@login_required
def private_area(request: HttpRequest) -> HttpResponse:
    # Aquí puedes añadir lógica para contar posts, ver fecha del último backup, etc.
    context: Dict[str, Any] = {
        'segment': 'dashboard', # Útil para marcar el menú activo
    }
    return render(request, 'private/pages/dashboard.html', context)

@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """
    Perfil de usuario en zona privada.
    Redirigimos a private_area que es la dashboard principal.
    """
    return redirect('private_area')

def home(request: HttpRequest) -> HttpResponse:
    # 1. GESTIÓN DEL FORMULARIO (POST)
    if request.method == 'POST':
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

    # 2. CARGA DE DATOS PARA LA LANDING (GET)
    # Recuperamos todos los objetos necesarios de la base de datos
    info: Optional[Info] = Info.objects.first()
    skills = Skill.objects.all()
    experiences = Experience.objects.all().order_by('-start_date') # Ordenados por fecha
    education = Education.objects.all()
    projects = Project.objects.all()
    latest_posts = Post.objects.filter(status='published').order_by('-publish')[:3]
    metrics = Metric.objects.filter(is_visible=True).order_by('order')
    
    # 3. CONSTRUCCIÓN DEL CONTEXTO
    context: Dict[str, Any] = {
        'info': info,
        'skills': skills,
        'experiences': experiences,
        'education': education,
        'projects': projects,
        'latest_posts': latest_posts,
        'metrics': metrics,
        'form': form,  # Pasamos el objeto form (con o sin errores) al HTML
    }

    # 4. RENDERIZADO
    # 4. RENDERIZADO
    return render(request, 'landing/pages/home.html', context)

def is_superuser(user) -> bool:
    return user.is_authenticated and user.is_superuser
    
@user_passes_test(is_superuser)
def export_data_view(request: HttpRequest) -> HttpResponse:
    """
    Exporta los datos de las apps landing y gym a un JSON descargable.
    Solo accesible por superusuarios.
    """
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
        action: Optional[str] = request.POST.get('action')
        
        if action == 'export':
            # Exportar datos a JSON descargable
            return export_data_view(request)
        elif action == 'view':
            # Redirigir al método que muestra el contenido del JSON
            # (aquí simplemente mostramos el JSON en la pantalla)
            logger.info(f"Backup view requested by {request.user}")
            messages.success(request, "Visualizando copia de seguridad.")
            return redirect('landing:private_area')
        elif action == 'restore':
            # TODO: Implementar lógica de restauración desde JSON subido
            logger.warning(f"Restore action not yet implemented (requested by {request.user})")
            messages.info(request, "La funcionalidad de restauración aún está en desarrollo.")
            return redirect('landing:private_area')
            
        return redirect('landing:private_area')
    
    # Si alguien intenta entrar por GET, lo mandamos de vuelta
    return redirect('landing:private_area')