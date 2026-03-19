# Guía de Referencia: Django Components UI

Este proyecto utiliza una librería personalizada de componentes de UI basada en `inclusion_tags` de Django y Tailwind CSS.

## Configuración Inicial
Para usar cualquier componente en una plantilla:
```django
{% load components_ui %}
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
| `{% comp_tabla %}` | `columns`, `rows`, `selectable` | Tabla dinámica con soporte para filas de datos. |
| `{% comp_tabs %}` | `tabs_data`, `active_tab` | `tabs_data=[{'title': '...', 'content': '...'}]` |
| `{% comp_acordeon %}` | `items`, `id` | `items=[{'title': '...', 'description': '...', 'icon': '...'}]` |
| `{% comp_carousel %}` | `items` | Carrusel visual con gradientes y navegación. |
| `{% comp_steps %}` | `steps`, `current_step` | `steps=[{'title': 'Paso 1'}, ...]` |
| `{% comp_breadcrumbs %}` | `items` | `items=[{'title': 'Home', 'url': '/'}, ...]` |
| `{% comp_navbar %}` | `title`, `links`, `show_user` | Barra de navegación superior. |
| `{% comp_sidebar_menu %}`| `menu_items` | Menú lateral colapsable con iconos. |
| `{% comp_map %}` | `center_lat`, `center_lng`, `zoom` | Mapa interactivo simulado o real. |
| `{% comp_chart %}` | `id`, `type` (bar/line), `data` | Integración con Chart.js. |

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
        
        {% comp_tabla columns=cols rows=users_list selectable=True %}
        
        <div class="flex justify-end gap-3">
            {% comp_button text="Cancelar" appearance="outlined" color="gray" %}
            {% comp_button text="Guardar Cambios" icon="CheckIcon" %}
        </div>
    </div>
{% endblock %}
```
