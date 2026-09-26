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
| Seguridad (HTML) | `bleach>=6.0.0` | Sanitización XSS de contenido CKEditor |
| Tareas Async | `celery>=5.3.0` + `redis>=5.0.0` | Batch PageViews en analytics, cleanup periódicos |
| CSP + Nonce | `django-csp>=3.7` | Nonce dinámico por request, ENFORCE mode |

---

## 3. Estructura de Aplicaciones

```
app/
├── config/          # settings.py, urls.py, wsgi.py, logging_config.py
├── landing/         # Hub principal, SEO global, Portal Privado (/private/)
├── blog/            # Engine de contenidos con SEO por post
├── documentum/      # Wiki técnica con navegación jerárquica (/wiki/)
├── gym/             # Seguimiento/inventario (Productos). Sistema de mantenimiento tabular
├── prompts/         # Biblioteca de prompts IA. Arquitectura No-DB (sincroniza con GitHub API)
└── analytics/       # Analytics Privacy-First + Blog Trending. Dashboards en /private/analytics/

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
- **Build Command** (Render):
  ```bash
  pip install -r requirements.txt && python manage.py migrate && python manage.py setup_db && python create_admin.py && python manage.py collectstatic --noinput
  ```
  - `python manage.py setup_db`: Verifica tablas críticas, restaura de backup si vacía, normaliza slugs, renderiza HTML
  - Automáticamente loguea estado de tablas al final para debugging en producción

### Diagnóstico en Producción (2026-09-26)

**Endpoint único de diagnóstico (Superuser only):**
- **URL**: `GET /api/debug/diagnostics/` (JSON)
- **Alternativa visual**: Accede a `/private/` → Ve el diagnostics panel si eres superuser
- **Qué valida**:
  - Database connection
  - Critical tables (analytics_pageview, analytics_sessiontracker, landing_menuitem, auth_user)
  - Module imports (app.analytics, app.celery, etc.)
  - Context processors (menu_int_processor)
  - Template rendering (private/pages/dashboard.html)

**Cuando hay error de template**, el diagnóstico mostrará:
- `error_type`: ej. `ValueError`, `TemplateDoesNotExist`
- `error_msg`: descripción del error
- `traceback_logged`: true (ver Render logs para traceback completo)

### Pre-deploy checklist (ejecutar siempre antes de merge a `main`)

```bash
# 1. Todos los tests pasan
PYTHONPATH=. python app/manage.py test

# 2. collectstatic no falla (detecta referencias a .map faltantes, imports rotos, etc.)
DEBUG=False SECRET_KEY=test PYTHONPATH=. python app/manage.py collectstatic --noinput --clear

# 3. Verificar URLs del proyecto
PYTHONPATH=. python app/manage.py verify_urls
```

> **Trampa habitual**: archivos JS de vendor con `//# sourceMappingURL=*.map` sin el `.map` correspondiente.
> WhiteNoise falla en `collectstatic` silenciosamente en local si no se usa `CompressedManifestStaticFilesStorage`.
> Ejecutar siempre el paso 2 con `DEBUG=False` para replicar las condiciones de producción.

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
| **[RECURRENTE]** Dejar comentarios `//# sourceMappingURL=*.map` en archivos JS de vendor sin incluir el `.map` | `CompressedManifestStaticFilesStorage` de WhiteNoise falla en `collectstatic` y rompe el deploy en Render. Al añadir/actualizar un vendor JS, eliminar siempre la línea `sourceMappingURL` si el `.map` no está presente |
| Poner claves de API reales (aunque sean de test) en `ci.yml` como literales | GitGuardian las detecta y bloquea el PR. Usar claves ficticias (`ci-fake-*`) cuando `SILENCED_SYSTEM_CHECKS` ya desactiva la validación, o referenciar `${{ secrets.* }}` |
| Añadir imports en ficheros sin verificar con ruff antes del commit | El lint de CI falla. Ejecutar siempre `ruff check app/ --select F401,F811,E711,E712` antes de mergear |
| Ejecutar `python manage.py` en CI sin `PYTHONPATH=$GITHUB_WORKSPACE` y sin apuntar a `app/manage.py` | Django no encuentra el módulo `app.*` porque el proyecto no está instalado. El CI usa `PYTHONPATH: ${{ github.workspace }}` y `python app/manage.py` |
| **[CRÍTICO]** Olvidar que requirements.txt DEBE estar actualizado y instalarse en producción | Produce ImportError y 500 errors en Render. Ejemplo: sentry-sdk en requirements.txt pero no instalado = /private/ inaccesible. Verificar: `pip install -r requirements.txt` en post-deploy Render |

---

## 12. Seguridad — Hallazgos Críticos (2026-09-25)

### FIX #1: XSS Protection via HTML Sanitization

**Problema:** 6 templates usaban `|safe` con contenido de CKEditor sin sanitizar.

**Implementación:**
- Creado `app/utils/sanitizers.py` con función `sanitize_html()` usando bleach
- Creado `app/utils/template_filters.py` con custom filter `|sanitize_html`
- Reemplazados todos los `|safe` en templates:
  - `app/blog/templates/blog/post_detail.html`
  - `app/templates/documentum/document_detail.html` (2 usos)
  - `app/templates/landing/components/resume.html` (2 usos)
  - `app/templates/landing/components/portfolio.html`
- Whitelist segura: `<p>`, `<br>`, `<strong>`, `<em>`, `<a>`, `<h1-h6>`, `<ul>`, `<ol>`, `<li>`, `<blockquote>`, `<code>`, `<pre>`, `<img>`, `<table>`
- Uso: `{{ content|sanitize_html }}` en lugar de `{{ content|safe }}`

### FIX #2: Analytics N+1 Query Problem — Batch Async with Celery

**Problema:** Middleware de analytics hacía CREATE por cada request (+100ms latencia).

**Implementación:**
- Creado `app/celery.py` para configurar Celery + Redis
- Creado `app/tasks.py` con tareas asincrónicas:
  - `batch_save_pageviews`: bulk_create de múltiples PageViews
  - `batch_save_sessions`: actualizar SessionTrackers en batch
  - `cleanup_old_pageviews`: eliminar datos >90 días (Celery Beat)
  - `cleanup_old_sessions`: eliminar sesiones >30 días
- Modificado `app/analytics/middleware.py`:
  - Acumula PageViews en `request._pageviews_batch`
  - Envía a Celery cuando `len(batch) >= ANALYTICS_BATCH_SIZE` (default: 10)
  - SessionTracker sigue siendo síncrono (crítico para sesiones)
  - Fallback: bulk_create sincrónico si Celery no disponible
- Configuración en `settings.py`:
  - `CELERY_BROKER_URL`: Redis (default: `redis://localhost:6379/0`)
  - `ANALYTICS_BATCH_SIZE = 10`
  - En DEBUG: `CELERY_TASK_ALWAYS_EAGER = True` para testing local

**Resultado esperado:** Latencia 100ms → 5ms en analytics.

### FIX #3: Content Security Policy — Nonce-Based ENFORCE Mode

**Problema:** CSP estaba en Report-Only mode; scripts inline no estaban protegidos.

**Implementación:**
- Creado `app/config/middleware.py` con `CSPNonceMiddleware`
  - Genera nonce único (16 bytes, base64 URL-safe) por request
  - Disponible como `{{ request.csp_nonce }}` en templates
- Cambio en `settings.py`:
  - Agregado `CSPNonceMiddleware` al MIDDLEWARE (después de CSPMiddleware)
  - Cambiado `CONTENT_SECURITY_POLICY_REPORT_ONLY` → `CONTENT_SECURITY_POLICY` (ENFORCE)
  - `script-src`: Incluye nonce y elimina `'unsafe-inline'` gradualmente
  - Agregado context processor `csp_nonce()`
- Actualizado `app/config/context_processors.py`:
  - Nuevo context processor `csp_nonce()` para pasar nonce a templates
- Actualización de templates con nonce:
  - `app/templates/landing/layouts/base.html` (2 scripts inline)
  - `app/templates/landing/components/resume.html` (1 script)
  - `app/templates/documentum/base_docs.html` (1 script)

**Uso en templates:**
```django
<script nonce="{{ csp_nonce }}">
    // Tu código inline aquí
</script>
```

**Notas:**
- SessionStorage/localStorage siguen accesibles (necesarios para AOS, Typed.js, etc)
- `style-src` sigue permitiendo `'unsafe-inline'` (necesario para Bootstrap, componentes)
- Para scripts externos: no necesitan nonce, se permiten vía whitelist (Google, GitHub CDN)

---

## 13. Protocol de Auto-Evolución

Este documento es un organismo vivo. Tras cada tarea completada con éxito o tras cada corrección del usuario, evalúa si es necesario actualizar estas reglas para evitar errores futuros o mejorar la eficiencia. Si detectas un patrón de error en el código actual, añade una regla "Anti-Pattern" inmediatamente.

**Cuándo actualizar este archivo:**
- El usuario corrige explícitamente una forma de programar → actualizar la sección afectada
- Se toma una decisión de cambio de librería o patrón → documentarlo en Tech Stack y Anti-Patterns
- Se detecta un error recurrente en peticiones → añadirlo como Anti-Pattern con `[RECURRENTE]`
- Se añade una nueva app al proyecto → documentar su responsabilidad en sección 3
- Se descubre un comportamiento específico del entorno (Render, Supabase) → añadir a sección 9 o 10
