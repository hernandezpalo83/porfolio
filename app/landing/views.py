from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Info, Skill, Experience, Education, Project, Contact


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