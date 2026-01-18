import requests
import base64
import json
import os
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE REPOSITORIO ---
GITHUB_REPO = "hernandezpalo83/AI-Prompts"
GITHUB_FILE_PATH = "index.json"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

def get_github_data():
    """
    Lee el archivo JSON desde GitHub API. Soporta repositorios PRIVADOS mediante PAT.
    Retorna: (lista_de_prompts, sha_actual)
    """
    token = os.getenv('GITHUB_TOKEN')
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # Usamos un parámetro aleatorio para bypass de caché de la API de GitHub
        response = requests.get(GITHUB_API_URL, headers=headers, params={'t': os.urandom(8).hex()})
        if response.status_code == 200:
            data = response.json()
            content_json = base64.b64decode(data['content']).decode('utf-8')
            return json.loads(content_json), data['sha']
        return [], None
    except Exception as e:
        logger.error(f"Error reading data from GitHub: {e}", exc_info=True)
        return [], None

def save_to_github(updated_data, commit_message):
    """
    Realiza un commit (PUT) en el repositorio con el nuevo contenido JSON.
    Requiere el SHA del archivo para evitar conflictos de escritura.
    """
    token = os.getenv('GITHUB_TOKEN')
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. Obtención de SHA actualizado antes de escribir
        get_res = requests.get(GITHUB_API_URL, headers=headers)
        if get_res.status_code != 200: return False
        current_sha = get_res.json()['sha']

        # 2. Codificación de datos
        json_content = json.dumps(updated_data, indent=4, ensure_ascii=False)
        base64_content = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')

        # 3. Envío de commit
        payload = {
            "message": commit_message,
            "content": base64_content,
            "sha": current_sha,
            "branch": "main"
        }

        put_res = requests.put(GITHUB_API_URL, headers=headers, json=payload)
        return put_res.status_code in [200, 201]
    except Exception as e:
        logger.error(f"Error writing data to GitHub: {e}", exc_info=True)
        return False

@login_required
def prompt_library(request):
    """
    Vista principal: Gestiona la visualización, creación y edición de prompts.
    """
    prompts_data, _ = get_github_data()

    if request.method == 'POST':
        edit_id = request.POST.get('id')
        new_prompt = {
            "title": request.POST.get('title'),
            "category": request.POST.get('category'),
            "description": request.POST.get('description'),
            "prompt": request.POST.get('prompt') 
        }

        # Lógica de actualización o creación
        if edit_id and edit_id.isdigit():
            idx = int(edit_id) - 1
            if 0 <= idx < len(prompts_data):
                prompts_data[idx] = new_prompt
                msg_user = f"Prompt '{new_prompt['title']}' actualizado."
                commit_msg = f"🔧 Edit: {new_prompt['title']} via Admin"
            else:
                prompts_data.append(new_prompt)
                msg_user = "Nuevo prompt creado."
                commit_msg = f"✨ Add: {new_prompt['title']} via Admin"
        else:
            prompts_data.append(new_prompt)
            msg_user = "Nuevo prompt creado."
            commit_msg = f"✨ Add: {new_prompt['title']} via Admin"

        # Sincronización con GitHub
        if save_to_github(prompts_data, commit_msg):
            messages.success(request, msg_user)
        else:
            messages.error(request, "Error de sincronización con el repositorio remoto.")
        
        return redirect('prompts:prompt_library')

    # Filtrado dinámico
    categories = sorted(list(set(p.get('category', 'Sin Categoría') for p in prompts_data)))
    query = request.GET.get('q', '').lower()
    category_filter = request.GET.get('category', 'all')

    if query:
        prompts_data = [p for p in prompts_data if query in p.get('title', '').lower() or query in p.get('description', '').lower()]
    if category_filter and category_filter != 'all':
        prompts_data = [p for p in prompts_data if p.get('category') == category_filter]

    return render(request, 'landing/private/layouts/prompts.html', {
        'prompts': prompts_data,
        'categories': categories,
        'selected_category': category_filter,
        'query': query
    })

@login_required
def delete_prompt(request, index):
    """
    Elimina un elemento del JSON por índice y realiza commit en GitHub.
    """
    prompts_data, _ = get_github_data()
    
    if prompts_data:
        try:
            idx = int(index) - 1
            if 0 <= idx < len(prompts_data):
                deleted_item = prompts_data.pop(idx)
                commit_msg = f"🗑️ Delete: {deleted_item.get('title')} via Admin"
                
                if save_to_github(prompts_data, commit_msg):
                    messages.success(request, f"Prompt '{deleted_item.get('title')}' eliminado.")
                else:
                    messages.error(request, "Error al actualizar el repositorio tras eliminar.")
            else:
                messages.error(request, "El prompt seleccionado no existe.")
        except Exception as e:
            messages.error(request, f"Fallo técnico: {e}")
    else:
        messages.error(request, "No se pudo acceder a los datos del repositorio.")

    return redirect('prompts:prompt_library')