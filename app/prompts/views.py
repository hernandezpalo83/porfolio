import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

@login_required
def prompt_library(request):
    # URL de tu index.json en el repositorio de AIPrompts
    JSON_URL = "https://raw.githubusercontent.com/hernandezpalo83/AI-Prompts/main/index.json"
    
    prompts_data = []
    categories = set()
    
    try:
        response = requests.get(JSON_URL)
        if response.status_code == 200:
            prompts_data = response.json()
            # Extraemos categorías únicas para el filtro
            categories = sorted(list(set(p['category'] for p in prompts_data)))
    except Exception as e:
        print(f"Error cargando prompts: {e}")

    # Lógica de búsqueda y filtrado
    query = request.GET.get('q', '').lower()
    category_filter = request.GET.get('category', '')

    if query:
        prompts_data = [
            p for p in prompts_data 
            if query in p['title'].lower() or query in p['description'].lower()
        ]
    
    if category_filter:
        prompts_data = [p for p in prompts_data if p['category'] == category_filter]

    context = {
        'prompts': prompts_data,
        'categories': categories,
        'query': query,
        'selected_category': category_filter,
    }
    
    return render(request, 'prompts/prompt_list.html', context)