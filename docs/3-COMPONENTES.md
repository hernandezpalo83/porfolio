# 🎨 Componentes UI — django-components-ui

**Catálogo completo de 52 componentes reutilizables. Siempre usa estos en lugar de escribir HTML manual.**

---

## Instalación

### Opción A: Vía SSH (Recomendado)
```bash
pip install git+ssh://git@github.com/hernandezpalo83/django-components-ui.git#subdirectory=django_components_ui
```

### Opción B: Copia directa
```bash
cp -r /ruta/django_components_ui app/django_components_ui
```

Registrar en `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'django_components_ui',
]
```

### Troubleshooting
- **`TemplateDoesNotExist: components_ui/...`** → Reinstalar en modo editable
- **`Invalid filter: 'to_json'`** → Actualizar librería desde repo fuente
- **Falta `MANIFEST.in`** → Verificar que el repo fuente lo incluya

---

## Requisitos del Layout

El archivo base debe incluir:

```html
<!-- HEAD -->
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://unpkg.com/tabulator-tables@6.2.1/dist/css/tabulator_modern.min.css" rel="stylesheet">

<!-- BODY (al final) -->
<script src="https://unpkg.com/tabulator-tables@6.2.1/dist/js/tabulator.min.js"></script>
<script src="{% static 'components_ui/js/components.js' %}"></script>
```

---

## Catálogo de Componentes (52)

### 1️⃣ Elementos Atómicos

| Componente | Propiedades | Descripción |
|---|---|---|
| `comp_button` | `text`, `appearance` (contained/outlined), `color`, `icon`, `size`, `href`, `disabled` | Botón premium con hover |
| `comp_icon` | `name` (Heroicon), `size`, `color`, `solid` (bool) | SVG optimizado |
| `comp_badge` | `text`, `color`, `type` (solid/outlined/light) | Etiqueta de estado |
| `comp_input_text` | `name`, `label`, `placeholder`, `icon`, `required`, `value` | Campo de texto con icono |
| `comp_toggle` | `name`, `label`, `checked` | Switch iOS/Material |
| `comp_card` | `title`, `subtitle`, `value`, `classes`, `children` | Contenedor con sombra |
| `comp_title` | `text`, `level` (1-6), `hr` (bool), `class` | Encabezado consistente |

### 2️⃣ Componentes de Layout

| Componente | Propiedades | Descripción |
|---|---|---|
| `comp_navbar` | `title`, `links`, `show_user`, `logo_url` | Barra de navegación superior |
| `comp_sidebar_menu` | `menu_items` | Menú lateral colapsable con iconos |
| `comp_tabs` | `tabs_data`, `active_tab` | Tabs con contenido variable |
| `comp_acordeon` | `items`, `id` | Acordeón expandible |
| `comp_steps` | `steps`, `current_step` | Indicador de pasos |
| `comp_breadcrumbs` | `items` | Migas de pan para navegación |
| `comp_carousel` | `items`, `autoplay` (bool), `interval` | Carrusel visual con gradientes |

### 3️⃣ Componentes de Datos

| Componente | Propiedades | Estructura esperada |
|---|---|---|
| **`comp_tabla`** | `columns`, `data_url`, `page_size`, `group_by`, `searchable`, `filterable`, `height` | Tabla **lectura** basada en Tabulator |
| **`comp_tabla_mantenimiento`** | `data_url`, `columns`, `create_url`, `searchable`, `filterable`, `group_by` | Tabla **CRUD** (editar, borrar, crear) basada en Tabulator |
| **`comp_tabla_informes`** | `data_url`, `columns`, `export_url`, `group_by`, `height`, `filterable` | Tabla **reportes** con mayor volumen |
| `comp_agenda` | `data_url`, `view_mode` (month/week/day) | Calendario interactivo |
| `comp_chart` | `id`, `type` (bar/line/pie), `data` | Integración Chart.js |
| `comp_map` | `center_lat`, `center_lng`, `zoom`, `markers` | Mapa interactivo |

### 4️⃣ Componentes de Formulario

| Componente | Propiedades | Descripción |
|---|---|---|
| `comp_input_text` | `name`, `label`, `placeholder`, `icon`, `required` | Campo de texto |
| `comp_input_email` | `name`, `label`, `placeholder` | Campo email validado |
| `comp_input_password` | `name`, `label`, `placeholder` | Campo password con toggle |
| `comp_select` | `name`, `label`, `options`, `selected` | Dropdown |
| `comp_textarea` | `name`, `label`, `placeholder`, `rows` | Área de texto multilínea |
| `comp_toggle` | `name`, `label`, `checked` | Checkbox estilizado |
| `comp_radio_group` | `name`, `label`, `options`, `selected` | Radio buttons |
| `comp_file_upload` | `name`, `label`, `accept`, `multiple` | Upload de archivos |

### 5️⃣ Componentes de Feedback

| Componente | Propiedades | Descripción |
|---|---|---|
| `comp_alert` | `message`, `type` (success/error/warning/info), `dismissible` | Alerta con color |
| `comp_toast` | `message`, `type`, `duration` | Notificación temporal |
| `comp_modal` | `title`, `content`, `actions` | Modal centrado |
| `comp_loading` | `message`, `type` (spinner/skeleton) | Indicador de carga |

### 6️⃣ Componentes Especiales

| Componente | Propiedades | Descripción |
|---|---|---|
| `comp_code_block` | `code`, `language` (python/js/html/sql), `copy_button` | Bloque de código con syntax highlight |
| `comp_timeline` | `events` | Línea de tiempo vertical |
| `comp_progress_bar` | `value`, `max`, `color`, `label` | Barra de progreso |
| `comp_stat_tile` | `title`, `value`, `unit`, `icon`, `trend` | Tarjeta de estadística |
| `comp_pill` | `text`, `removable`, `onClick` | Píldora (chip) interactiva |
| `comp_avatar` | `src`, `size`, `name`, `fallback_icon` | Avatar de usuario |
| `comp_badge_list` | `items` | Lista de badges |
| `comp_link_card` | `title`, `description`, `href`, `icon` | Tarjeta de enlace |
| `comp_pricing_table` | `plans` | Tabla de precios |
| `comp_feature_list` | `features` | Lista de características |
| `comp_testimonial` | `quote`, `author`, `role`, `avatar` | Testimonial con avatar |
| `comp_faq` | `items` | FAQ acordeón |

---

## Reglas de uso

### 1. Prioridad absoluta
Siempre usa componentes de `components_ui` en lugar de escribir HTML/Tailwind manual para elementos comunes.

### 2. Datos dinámicos
Los componentes como `tabs`, `acordeon`, `steps` esperan listas de diccionarios:
```python
# En la vista:
tabs_data = [
    {"title": "Pestaña 1", "content": "<p>Contenido 1</p>"},
    {"title": "Pestaña 2", "content": "<p>Contenido 2</p>"},
]
return render(request, "...", {"tabs_data": tabs_data})
```

```django
{# En la plantilla #}
{% comp_tabs tabs_data=tabs_data active_tab=0 %}
```

### 3. Iconos — Siempre Heroicons v2
Nombres como: `HomeIcon`, `ChartBarIcon`, `UsersIcon`, `Cog6ToothIcon`, etc.

```django
{% comp_button text="Descargar" icon="ArrowDownTrayIcon" color="primary" %}
```

### 4. Colores disponibles
`primary`, `success`, `error`, `warning`, `blue`, `indigo`, `purple`, `pink`, `red`, `orange`, `yellow`, `green`, `teal`, `cyan`, `gray`

---

## Ejemplo: Tabla de Mantenimiento Completa

```python
# views.py
def mantenimiento_productos(request):
    columnas = [
        {"title": "ID", "field": "id", "width": 70, "editor": False},
        {"title": "Nombre", "field": "nombre", "headerFilter": "input"},
        {"title": "Precio", "field": "precio", "editor": "number"},
        {"title": "Estado", "field": "estado", "editor": "select", "editorParams": {
            "values": {"activo": "Activo", "inactivo": "Inactivo"}
        }},
        {"title": "Acciones", "formatter": "buttonCross", "width": 100, "hozAlign": "center"},
    ]
    return render(request, "gym/mantenimiento.html", {
        "titulo": "Mantenimiento de Productos",
        "descripcion": "Gestión completa de inventario",
        "cols": columnas,
        "api_url": "/gym/api/producto-api/"
    })
```

```django
{# gym/mantenimiento.html #}
{% extends 'private/layouts/base.html' %}
{% load components_ui %}

{% block content %}
<div class="card card-gemini shadow-sm p-4">
    <h2>{{ titulo }}</h2>
    <p class="text-muted">{{ descripcion }}</p>
    
    {% comp_tabla_mantenimiento 
        data_url=api_url 
        columns=cols 
        searchable=True 
        filterable=True 
    %}
</div>
{% endblock %}
```

---

## Referencias
- **Documentación oficial**: `COMPONENTS_AI_GUIDE.md` (antes de la consolidación)
- **Tabulator JS docs**: https://tabulator.info/
- **Heroicons**: https://heroicons.com/

