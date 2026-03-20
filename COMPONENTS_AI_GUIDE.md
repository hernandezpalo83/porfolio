# Guía de Referencia: Django Components UI

Este proyecto utiliza una librería personalizada de componentes de UI basada en `inclusion_tags` de Django y Tailwind CSS.

## Métodos de Instalación

### Opción A: Vía Git (Recomendado para producción privada)
Puedes instalar la librería directamente desde tu repositorio remoto. Como la librería está dentro de una subcarpeta, usa el parámetro `subdirectory`:

**1. Vía HTTPS (Con Token):**
```bash
pip install git+https://TU_TOKEN@github.com/tu-usuario/tu-repo.git#subdirectory=django_components_ui
```

**2. Vía SSH (Más seguro, no requiere tokens harcodeados):**
```bash
pip install git+ssh://git@github.com/tu-usuario/tu-repo.git#subdirectory=django_components_ui
```

**En `requirements.txt` (usando SSH):**
```text
django-components-ui @ git+ssh://git@github.com/tu-usuario/tu-repo.git#subdirectory=django_components_ui
```

> [!NOTE]
> Si el repositorio es privado, asegúrate de configurar un SSH key o usar un Personal Access Token (PAT) en la URL.

### Opción B: Copia Directa
1. **Copia la carpeta** `django_components_ui` a la raíz de tu nuevo proyecto.
2. **Regístrala** en `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       ...
       'django_components_ui',
   ]
   ```

## Estándares de Diseño
- **Framework**: Tailwind CSS (obligatorio para el estilado).
- **Iconos**: Heroicons v2 (nombres como `HomeIcon`, `ChartBarIcon`, `UsersIcon`).
- **Colores**: Soporta `primary`, `success`, `error`, `warning`, `blue`, `indigo`, etc.

## Listado de Componentes (52 Disponibles)

### 1. Elementos Atómicos (Bloques base)
| Tag | Propiedades Principales | Descripción |
|-----|-------------------------|-------------|
| `{% comp_button %}` | `text`, `appearance` (contained/outlined), `color`, `icon`, `size` | Botón premium con hover y estados. |
| `{% comp_icon %}` | `name` (Heroicon), `size`, `color`, `solid` (bool) | Renderizado de SVG optimizado. |
| `{% comp_badge %}` | `text`, `color`, `type` (solid/outlined/light) | Etiquetas de estado. |
| `{% comp_input_text %}` | `name`, `label`, `placeholder`, `icon`, `required` | Campo de texto con icono integrado. |
| `{% comp_toggle %}` | `name`, `label`, `checked` | Switch tipo iOS/Material. |
| `{% comp_card %}` | `title`, `subtitle`, `value`, `classes` | Contenedor con sombra y bordes suaves. |
| `{% comp_title %}` | `text`, `level` (1-6), `hr` (bool) | Encabezados consistentes. |

### 2. Componentes Complejos (Layout y Datos)
| Tag | Propiedades Principales | Estructura de Datos |
|-----|-------------------------|----------------------|
| `{% comp_agenda %}` | `data_url`, `view_mode` | Visualización de calendario (vía JS o Mock). |
| `{% comp_tabla %}` | `columns`, `data_url`, `page_size`, `group_by`, `searchable`, `filterable`, `height` | Tabla interactiva basada en **Tabulator** con soporte para agrupaciones, filtros por columna y búsqueda global. |
| `{% comp_tabla_mantenimiento %}` | `data_url`, `columns`, `create_url`, `group_by`, `searchable`, `filterable` | Versión para gestión (CRUD) basada en **Tabulator JS**. Permite edición, borrado y creación desde la misma interfaz. |
| `{% comp_tabla_informes %}` | `data_url`, `columns`, `export_url`, `group_by`, `height`, `filterable` | Versión para reportes con mayor volumen de datos y altura configurable. |
| `{% comp_tabs %}` | `tabs_data`, `active_tab` | `tabs_data=[{'title': '...', 'content': '...'}]` |
| `{% comp_acordeon %}` | `items`, `id` | `items=[{'title': '...', 'description': '...', 'icon': '...'}]` |
| `{% comp_carousel %}` | `items` | Carrusel visual con gradientes y navegación. |
| `{% comp_steps %}` | `steps`, `current_step` | `steps=[{'title': 'Paso 1'}, ...]` |
| `{% comp_breadcrumbs %}` | `items` | `items=[{'title': 'Home', 'url': '/'}, ...]` |
| `{% comp_navbar %}` | `title`, `links`, `show_user` | Barra de navegación superior. |
| `{% comp_sidebar_menu %}`| `menu_items` | Menú lateral colapsable con iconos. |
| `{% comp_map %}` | `center_lat`, `center_lng`, `zoom` | Mapa interactivo simulado o real. |
| `{% comp_chart %}` | `id`, `type` (bar/line), `data` | Integración con Chart.js. |
| `{% comp_mantenimiento %}` | `titulo`, `descripcion`, `api_url`, `columnas` | Componente de página completa para mantenimientos simples. |

## Reglas para la IA
1. **Prioridad**: Siempre usa estos componentes en lugar de escribir HTML/Tailwind desde cero para elementos comunes.
2. **Datos Complejos**: Los componentes como `tabs`, `acordeon` y `steps` esperan listas de diccionarios. Si no tienes los datos reales, créalos siguiendo la estructura `[{'title': '...', ...}]`.
3. **Iconos**: Usa siempre los nombres de Heroicons v2 terminados en `Icon` (ej. `Cog6ToothIcon`).
4. **Layout**: Usa `comp_card` para envolver secciones de contenido y `comp_title` para los nombres de las vistas.

## Ejemplo de Página Completa
```django
{% extends "base.html" %}
{% load components_ui %}

{% block content %}
    <div class="p-8 space-y-6">
        {% comp_title text="Gestión de Usuarios" level=1 hr=True %}
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            {% comp_card title="Total" value="1,240" color="primary" %}
            {% comp_card title="Activos" value="1,100" color="success" %}
        </div>

        {% comp_tabs tabs_data=my_tabs %}
        
        {% comp_tabla columns=cols data_url="/api/users/" selectable=True group_by="role" searchable=True %}
        
        <div class="flex justify-end gap-3">
            {% comp_button text="Cancelar" appearance="outlined" color="gray" %}
            {% comp_button text="Guardar Cambios" icon="CheckIcon" %}
        </div>
    </div>
{% endblock %}
```
## Solución de Problemas (Troubleshooting)

### 1. Error: `TemplateDoesNotExist: components_ui/elementos/title.html`
- **Causa**: La librería instalada vía `pip` puede no incluir la carpeta `templates`.
- **Solución**: Seguir la **Opción B (Copia Directa)**. Copiar la carpeta `components_ui` íntegra a `app/components_ui` y registrarla en `INSTALLED_APPS` como `app.components_ui`. Esto asegura que las plantillas se carguen desde el sistema de archivos del proyecto.

### 2. Error: `Invalid filter: 'to_json'`
- **Causa**: El filtro `to_json` es necesario para pasar configuraciones complejas (como columnas de Tabulator) al componente. Si no está definido en `templatetags/components_ui.py`, fallará.
- **Solución**: Asegurarse de que `app/components_ui/templatetags/components_ui.py` incluya:
  ```python
  import json
  from django.utils.safestring import mark_safe
  @register.filter
  def to_json(value):
      return mark_safe(json.dumps(value))
  ```

---
> [!IMPORTANT]
> Siempre revisa que la versión local de `components_ui` en `app/` esté sincronizada con la del repositorio de componentes si realizas cambios estructurales.
