from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Info, Skill, Experience, Education, Project, Contact
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.contrib.auth.decorators import user_passes_test
import io

def error_404_view(request, exception):
    return render(request, 'landing/404.html', status=404)

def home(request):
    return render(request, 'landing/index.html')

@login_required
def private_area(request):
    # Definimos los módulos que quieres mostrar en el Dashboard
    # 'url_name' debe coincidir con el 'name' definido en tus urlpatterns
    modules = [
        {
            'title': 'Biblioteca de Prompts',
            'description': 'Gestor avanzado de prompts estructurados para Product Managers.',
            'url_name': 'prompt_library',
            'icon': 'bi-cpu-fill', # Iconos de Bootstrap
            'category': 'AI & Strategy'
        },
        {
            'title': 'Catálogo Gym',
            'description': 'Gestión de productos y stock para el módulo de gimnasio.',
            'url_name': 'lista_productos',
            'icon': 'bi-cart-check-fill',
            'category': 'Management'
        },
        {
            'title': 'Tabla de Productos (HTMX)',
            'description': 'Vista técnica avanzada con filtrado dinámico mediante HTMX.',
            'url_name': 'product_list',
            'icon': 'bi-table',
            'category': 'Management'
        },
    ]

    return render(request, 'landing/private.html', {'modules': modules})

@login_required
def profile(request):
    return render(request, 'landing/profile.html')

def home(request):
    info = Info.objects.first()
    skills = Skill.objects.all()
    experiences = Experience.objects.all()
    education = Education.objects.all()
    projects = Project.objects.all()
    contact = Contact.objects.first()
    context = {
        'info': info,
        'skills': skills,
        'experiences': experiences,
        'education': education,
        'projects': projects,
        'contact': contact,
    }
    return render(request, 'landing/index.html', context)

def is_superuser(user):
    return user.is_authenticated and user.is_superuser
    
@user_passes_test(is_superuser)
def export_data_view(request):
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