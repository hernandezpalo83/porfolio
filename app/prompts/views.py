import requests
import base64
import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def save_to_github(updated_data):
    """
    Sincroniza el JSON actualizado con el repositorio de GitHub.
    Utiliza el SHA actual para permitir la sobreescritura.
    """
    token = os.getenv('GITHUB_TOKEN')
    repo = "hernandezpalo83/AI-Prompts"
    path = "index.json"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. Obtener el SHA del archivo actual (imprescindible para actualizar)
        get_res = requests.get(url, headers=headers)
        if get_res.status_code != 200:
            print(f"Error obteniendo SHA: {get_res.status_code} - {get_res.text}")
            return False
        
        current_sha = get_res.json()['sha']

        # 2. Preparar el contenido (JSON -> UTF-8 -> Base64)
        json_content = json.dumps(updated_data, indent=4, ensure_ascii=False)
        base64_content = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')

        # 3. Realizar el PUT (Update)
        data = {
            "message": "Update prompts library via HernandezPalo Admin",
            "content": base64_content,
            "sha": current_sha,
            "branch": "main"
        }

        put_res = requests.put(url, headers=headers, json=data)
        if put_res.status_code not in [200, 201]:
            print(f"Error en PUT GitHub: {put_res.status_code} - {put_res.text}")
            return False
        
        return True

    except Exception as e:
        print(f"Excepción en save_to_github: {e}")
        return False

@login_required
def prompt_library(request):
    # Bypass de caché para leer siempre lo último de GitHub
    JSON_URL = "https://raw.githubusercontent.com/hernandezpalo83/AI-Prompts/main/index.json?nocache=1"
    prompts_data = []
    
    # 1. CARGA DE DATOS
    try:
        response = requests.get(JSON_URL)
        if response.status_code == 200:
            prompts_data = response.json()
    except Exception as e:
        print(f"Error cargando JSON: {e}")

    # 2. PROCESAMIENTO DEL FORMULARIO (POST)
    if request.method == 'POST':
        edit_id = request.POST.get('id')
        
        # Sincronizamos con la clave 'prompt' que usa tu index.json
        new_prompt = {
            "title": request.POST.get('title'),
            "category": request.POST.get('category'),
            "description": request.POST.get('description'),
            "prompt": request.POST.get('prompt') 
        }

        if edit_id and edit_id.isdigit():
            # Lógica UPDATE
            try:
                idx = int(edit_id) - 1
                if 0 <= idx < len(prompts_data):
                    prompts_data[idx] = new_prompt
                    msg_text = f"Prompt '{new_prompt['title']}' actualizado."
                else:
                    prompts_data.append(new_prompt)
                    msg_text = "Nuevo prompt creado."
            except ValueError:
                prompts_data.append(new_prompt)
                msg_text = "Nuevo prompt creado."
        else:
            # Lógica CREATE
            prompts_data.append(new_prompt)
            msg_text = "Nuevo prompt creado correctamente."

        # Sincronización Real con el Repositorio
        if save_to_github(prompts_data):
            messages.success(request, msg_text)
        else:
            messages.error(request, "Error de comunicación con GitHub. Revisa el TOKEN y los permisos del repo.")
        
        return redirect('prompts:prompt_library')

    # 3. FILTRADO Y CATEGORÍAS
    # Usamos .get() para evitar errores si faltan llaves en el JSON
    categories = sorted(list(set(p.get('category', 'Sin Categoría') for p in prompts_data)))
    query = request.GET.get('q', '').lower()
    category_filter = request.GET.get('category', 'all')

    if query:
        prompts_data = [
            p for p in prompts_data 
            if query in p.get('title', '').lower() or query in p.get('description', '').lower()
        ]
    
    if category_filter and category_filter != 'all':
        prompts_data = [p for p in prompts_data if p.get('category') == category_filter]

    context = {
        'prompts': prompts_data,
        'categories': categories,
        'selected_category': category_filter,
        'query': query
    }
    return render(request, 'landing/private/layouts/prompts.html', context)

@login_required
def delete_prompt(request, index):
    """
    Elimina un prompt basado en su índice y sincroniza con GitHub.
    """
    JSON_URL = "https://raw.githubusercontent.com/hernandezpalo83/AI-Prompts/main/index.json?nocache=1"
    
    try:
        response = requests.get(JSON_URL)
        if response.status_code == 200:
            prompts_data = response.json()
            
            idx = int(index) - 1
            if 0 <= idx < len(prompts_data):
                deleted_item = prompts_data.pop(idx)
                
                if save_to_github(prompts_data):
                    messages.success(request, f"Prompt '{deleted_item.get('title')}' eliminado del repositorio.")
                else:
                    messages.error(request, "No se pudo actualizar GitHub tras eliminar.")
            else:
                messages.error(request, "Índice de prompt no válido.")
    except Exception as e:
        messages.error(request, f"Error en el borrado: {e}")

    return redirect('prompts:prompt_library')