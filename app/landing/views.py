from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Info, Skill, Experience, Education, Project, Contact
from app.blog.models import Post
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
    # Aquí puedes añadir lógica para contar posts, ver fecha del último backup, etc.
    context = {
        'segment': 'dashboard', # Útil para marcar el menú activo
    }
    return render(request, 'landing/private/layouts/private_dashboard.html', context)

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
    latest_posts = Post.objects.filter(status='published').order_by('-publish')[:5]
    
    # 3. CONSTRUCCIÓN DEL CONTEXTO
    context = {
        'info': info,
        'skills': skills,
        'experiences': experiences,
        'education': education,
        'projects': projects,
        'latest_posts': latest_posts,
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

@login_required
@user_passes_test(lambda u: u.is_superuser) # Seguridad: solo superusuarios
def db_backup(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'export':
            # TODO: Aquí programaremos la lógica de exportación real
            # Por ahora, simulamos el éxito para validar la ruta
            messages.success(request, "Copia de seguridad solicitada correctamente.")
            
        return redirect('landing:private_area')
    
    # Si alguien intenta entrar por GET, lo mandamos de vuelta
    return redirect('landing:private_area')