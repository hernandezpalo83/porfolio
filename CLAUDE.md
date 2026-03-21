# CLAUDE.md — HernandezPalo Portfolio
> Documento de referencia definitivo para Claude Code. Léelo completo antes de proponer cualquier cambio.

---

## 1. Project DNA

Portfolio profesional de Javier Hernández Martin (hernandezpalo.es), construido como un **CMS Técnico Escalable** bajo el estándar **TPM (Technical Product Management)**. El objetivo es demostrar capacidades full-stack reales: arquitectura resiliente, SEO avanzado, automatización y gestión de producto técnico.

**No es un proyecto de demostración simple**. Cada decisión técnica tiene intencionalidad estratégica y debe mantenerse.

---

## 2. Tech Stack

| Capa | Tecnología | Notas |
|---|---|---|
| Backend | Django 5.1+ / Python 3.11+ | Sin Django REST Framework para vistas públicas |
| API (privada) | Django REST Framework (DRF) | Solo para endpoints de mantenimiento Tabulator |
| DB (prod) | PostgreSQL — Supabase (session pooler + SSL) | `dj-database-url` |
| DB (local/test) | SQLite | Auto-detectado si no hay `DATABASE_URL` |
| Frontend público | Vanilla JS ES6+, Custom CSS (Kards), sin jQuery | Máxima performance |
| Frontend privado | Bootstrap 5.3 + Bootstrap Icons | Glassmorphism `.card-gemini` |
| Componentes UI | `django-components-ui` (librería privada GitHub) | Ver sección 6 |
| Tablas interactivas | Tabulator JS 6.2.1 | Solo en área privada |
| Rich Text | CKEditor 5 (`django-ckeditor-5`) | Modelos `landing`, `blog`, `documentum` |
| Estáticos prod | WhiteNoise + `CompressedManifestStaticFilesStorage` | Cache 1 año |
| Minificación | `django-htmlmin` | Solo en producción (`HTML_MINIFY = not DEBUG`) |
| Despliegue | Render (Web Service) + CI/CD desde rama `main` | |
| CDN Assets | `https://raw.githubusercontent.com/hernandezpalo83/cdn/main` | `BRAND_ASSETS_URL` en settings |

---

## 3. Estructura de Aplicaciones

```
app/
├── config/          # settings.py, urls.py, wsgi.py, logging_config.py
├── landing/         # Hub principal, SEO global, Portal Privado (/private/)
├── blog/            # Engine de contenidos con SEO por post
├── documentum/      # Wiki técnica con navegación jerárquica (/wiki/)
├── gym/             # Seguimiento/inventario (Productos). Sistema de mantenimiento tabular
└── prompts/         # Biblioteca de prompts IA. Arquitectura No-DB (sincroniza con GitHub API)

app/templates/
├── landing/         # Tailwind + components_ui (área pública)
├── private/         # Bootstrap 5 (área privada, login requerido)
│   └── layouts/base.html  # Layout base del portal interno
├── documentum/      # Wiki
└── robots.txt
```

**Regla de namespacing de URLs:** `blog:`, `gym:`, `wiki:`. Las vistas privadas de `landing` usan el patrón `landing:private_*`.

---

## 4. Dual-Stack UI — NUNCA MEZCLAR

### A. Área Pública (`/`, `/blog/`, `/wiki/`)
- **CSS**: Tailwind CSS (CDN en desarrollo, nunca en producción sin build)
- **Componentes**: `{% load components_ui %}` + tags `comp_*`
- **Iconos**: Heroicons v2 (nombres como `HomeIcon`, `CheckIcon`)
- **JS**: Vanilla ES6+, cero jQuery

### B. Área Privada (`/private/`)
- **CSS**: Bootstrap 5.3 + `private_portal.css`
- **Estética**: Glassmorphism → clase `.card-gemini`, `.rounded-pill`, `.rounded-4`
- **Iconos**: Bootstrap Icons (`bi-shield-lock-fill`, `bi-box-arrow-up-right`)
- **Tablas**: Tabulator JS vía `comp_tabla_mantenimiento`
- **No usar Tailwind aquí, nunca**

---

## 5. Arquitectura de Código

### Patrón de Vistas
- Vistas simples: funciones con type hints (`HttpRequest → HttpResponse`)
- No se usa Class-Based Views genéricas salvo `FilterView` de `django-filters`
- Lógica de negocio mínima: los modelos validan con `clean()`, las vistas solo coordinan

### Modelos — Convenciones
- Validación siempre en `clean()`, nunca en la vista
- `IntegerChoices` / `TextChoices` para campos con opciones (ver `Producto.Estado`)
- `Meta.ordering` siempre definido
- `__str__` siempre implementado
- Campos de auditoría: `fecha_creacion = auto_now_add`, `created_at = auto_now_add`
- Idioma de campos: **español** en `gym`/`landing`, **inglés** en `blog`

### API (DRF) — Solo para mantenimiento interno
- Un `ViewSet` por modelo (`ModelViewSet`)
- Mixin `MetadataMixin` en `api.py` expone `/metadata/` para descubrir campos dinámicamente
- Serializers en `serializers.py` con `fields = '__all__'` como default
- Los endpoints siguen el patrón `/<app>/api/<modelo>-api/`

### Sistema de Mantenimiento Tabular (receta canónica)
Para cualquier CRUD rápido de un modelo en el portal interno:

1. **`serializers.py`** → `ModelSerializer` con `fields = '__all__'`
2. **`api.py`** → `MetadataMixin + ModelViewSet`
3. **`views.py`** → función que pasa `columnas` (config Tabulator) + `api_url`
4. **Plantilla** → extiende `private/layouts/base.html`, usa `comp_tabla_mantenimiento`

```python
# views.py
def mantenimiento_mi_modelo(request: HttpRequest) -> HttpResponse:
    columnas = [
        {"title": "ID", "field": "id", "width": 70, "editor": False},
        {"title": "Nombre", "field": "nombre", "headerFilter": "input"},
        # ... columnas según Tabulator JS docs
    ]
    return render(request, "mi_app/mantenimiento_generico.html", {
        "titulo": "Mantenimiento de X",
        "descripcion": "Gestión completa de X.",
        "cols": columnas,
        "api_url": "/mi_app/api/mi-modelo/"
    })
```

```django
{# plantilla #}
{% extends 'private/layouts/base.html' %}
{% load components_ui %}
{% block content %}
    <div class="card card-gemini shadow-sm p-4">
        {% comp_tabla_mantenimiento data_url=api_url columns=cols searchable=True filterable=True %}
    </div>
{% endblock %}
```

---

## 6. Librería `django-components-ui`

Librería privada instalada desde GitHub. Si falla la instalación:
- Verificar `MANIFEST.in` en el repositorio fuente (debe incluir plantillas y estáticos)
- En local, usar modo editable: `pip install -e /ruta/django_components_ui/`

**Error `TemplateDoesNotExist: components_ui/...`** → reinstalar en modo editable.
**Error `Invalid filter: 'to_json'`** → actualizar la librería desde el repo fuente.

Componentes clave:
- `comp_tabla_mantenimiento` — CRUD tabular (Tabulator)
- `comp_tabla` — lectura de datos
- `comp_button`, `comp_card`, `comp_title`, `comp_badge`, `comp_icon`
- `comp_tabs`, `comp_acordeon`, `comp_steps`, `comp_breadcrumbs`

**Regla**: usar siempre estos tags en lugar de HTML/Tailwind manual para elementos comunes.

---

## 7. SEO — Obligatorio en vistas públicas

- Cada vista pública **debe** tener: `<title>`, `<meta name="description">`, Open Graph tags
- Nuevas apps con contenido público **deben** registrar su sitemap en `app/config/urls.py` → dict `sitemaps`
- Imágenes en formato `.webp` usando CDN `BRAND_ASSETS_URL`
- No añadir librerías pesadas en el área pública
- `htmlmin` está activo en producción: evitar comentarios HTML innecesarios

---

## 8. Logging

**Nunca usar `print()`**. Usar el módulo `logging`:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detalle técnico")
logger.info("Evento de negocio relevante")
logger.warning("Situación inesperada pero recuperable")
logger.error("Fallo que requiere atención", exc_info=True)
```

- Configuración centralizada en `app/config/logging_config.py`
- Handlers: `console` (desarrollo) + `RotatingFileHandler` a `app/logs/django.log` (producción, 10MB × 5)
- Loggers configurados por app: `app.landing`, `app.blog`, `app.gym`, `app.prompts`

---

## 9. Resiliencia y Backup (Crítico para Render)

La BD de Render (free tier) tiene persistencia limitada. El proyecto implementa:

- **Backup manual**: botón en `/private/` → ejecuta `dumpdata` a `db_backup.json`
- **Restauración automática**: `python manage.py setup_db` detecta BD vacía y carga `db_backup.json`
- **Seed completo**: `python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render`

**Regla**: Al modificar modelos de `gym` o `landing`, recordar que los datos se persisten vía `db_backup.json`. Avisar al usuario si un cambio de schema puede romper la restauración.

---

## 10. Despliegue

- CI/CD automático desde rama `main` en Render
- Variables de entorno obligatorias: `SECRET_KEY`, `DATABASE_URL`, `DEBUG=False`, `ALLOWED_HOSTS`, `GITHUB_TOKEN_COMPONENTES`, `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY`
- Post-deploy (one-off en Render):
  ```bash
  pip install -r requirements.txt && python manage.py migrate && python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render && python create_admin.py && python manage.py collectstatic --noinput
  ```

---

## 11. Testing

```bash
python manage.py test               # todos los tests
python manage.py test app.documentum # solo documentum
python manage.py verify_urls        # verificación de URLs (pre-commit)
```

- Tests de integración obligatorios para cambios en `setup_db` o lógica de seed/normalización
- SQLite en local/CI, PostgreSQL solo en producción

---

## 12. Anti-Patterns — Prohibido

| Anti-Pattern | Motivo |
|---|---|
| Usar `print()` en lugar de `logging` | Logs no estructurados, no rotan, no configurables |
| Mezclar Bootstrap y Tailwind en la misma plantilla | Doble carga de CSS, conflictos de estilos |
| Crear vistas públicas sin meta SEO ni sitemap | Perjudica indexación, viola la TPM strategy |
| Lógica de negocio en las vistas | Debe ir en `clean()` del modelo o en un servicio |
| Usar jQuery en el área pública | Viola el principio de performance extrema |
| Hardcodear URLs de CDN en plantillas | Usar `BRAND_ASSETS_URL` / `PERSONAL_BRAND` de settings |
| Usar Tailwind CDN en producción sin build | Warning en consola, no se usa PurgeCSS |
| Crear modelos sin `__str__`, `Meta.ordering`, ni `clean()` | Incoherencia con el resto del codebase |
| Instalar paquetes sin añadirlos a `requirements.txt` | Rompe el despliegue en Render |
| Crear una nueva vista de mantenimiento sin seguir la receta canónica | Inconsistencia con el sistema Tabulator |

---

## 13. Protocol de Auto-Evolución

Este documento es un organismo vivo. Tras cada tarea completada con éxito o tras cada corrección del usuario, evalúa si es necesario actualizar estas reglas para evitar errores futuros o mejorar la eficiencia. Si detectas un patrón de error en el código actual, añade una regla "Anti-Pattern" inmediatamente.

**Cuándo actualizar este archivo:**
- El usuario corrige explícitamente una forma de programar → actualizar la sección afectada
- Se toma una decisión de cambio de librería o patrón → documentarlo en Tech Stack y Anti-Patterns
- Se detecta un error recurrente en peticiones → añadirlo como Anti-Pattern con `[RECURRENTE]`
- Se añade una nueva app al proyecto → documentar su responsabilidad en sección 3
- Se descubre un comportamiento específico del entorno (Render, Supabase) → añadir a sección 9 o 10
