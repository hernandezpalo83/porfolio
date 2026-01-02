from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Info, Skill, Experience, Education, Project, Contact
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.contrib.auth.decorators import user_passes_test
from .forms import FormularioContacto
from django.contrib import messages
from django.shortcuts import render, redirect


import io

def error_404_view(request, exception):
    return render(request, 'landing/404.html', status=404)

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
            # imprimimos los errores en la terminal para que puedas debuguear
            print("LOG DEBUG - Errores en el formulario:", form.errors)
            messages.error(request, 'Hubo un problema con el envío. Por favor, revisa los campos y el captcha.')
    else:
        # Carga inicial de la página
        form = FormularioContacto()

    # 2. CARGA DE DATOS PARA LA LANDING (GET)
    # Recuperamos todos los objetos necesarios de la base de datos
    info = Info.objects.first()
    skills = Skill.objects.all()
    experiences = Experience.objects.all().order_by('-start_date') # Ordenados por fecha
    education = Education.objects.all()
    projects = Project.objects.all()

    # 3. CONSTRUCCIÓN DEL CONTEXTO
    context = {
        'info': info,
        'skills': skills,
        'experiences': experiences,
        'education': education,
        'projects': projects,
        'form': form,  # Pasamos el objeto form (con o sin errores) al HTML
    }

    # 4. RENDERIZADO
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