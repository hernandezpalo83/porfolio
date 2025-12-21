from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Info, Skill, Experience, Education, Project, Contact

def home(request):
    return render(request, 'landing/index.html')


@login_required
def private_area(request):
    return render(request, 'landing/private.html')

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