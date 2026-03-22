# hernandezpalo.es — Portfolio Técnico

Portfolio profesional de **Javier Hernández Martin**, Technical Product Manager Senior.
Construido como un **CMS Técnico Escalable** que demuestra capacidades full-stack reales: arquitectura resiliente, SEO avanzado, automatización y gestión de producto técnico.

**Sitio en producción:** [hernandezpalo.es](https://hernandezpalo.es)

---

## Stack Técnico

| Capa | Tecnología |
|------|------------|
| Backend | Django 5.1 · Python 3.11+ |
| Base de datos (prod) | PostgreSQL — Supabase (session pooler + SSL) |
| Base de datos (local/test) | SQLite (auto-detectada) |
| Frontend público | Vanilla JS ES6+ · Custom CSS (Kards) · Sin jQuery |
| Frontend privado | Bootstrap 5.3 · Bootstrap Icons · Glassmorphism |
| Componentes UI | `django-components-ui` (librería privada, 46+ componentes) |
| Tablas interactivas | Tabulator JS 6.2.1 |
| Rich Text | CKEditor 5 (`django-ckeditor-5`) |
| Estáticos (prod) | WhiteNoise + `CompressedManifestStaticFilesStorage` (cache 1 año) |
| Minificación | `django-htmlmin` (solo en producción) |
| API interna | Django REST Framework (solo endpoints privados con `IsAuthenticated`) |
| Despliegue | Render (Web Service) · CI/CD desde rama `main` |
| CDN Assets | GitHub CDN (`BRAND_ASSETS_URL` en settings) |

---

## Arquitectura de Apps

```
app/
├── config/          # settings (modular: base/dev/prod/test), urls, wsgi, logging
├── landing/         # Hub principal · SEO global · Portal privado (/private/)
├── blog/            # CMS de posts con SEO por post · RSS ready
├── documentum/      # Wiki técnica con navegación jerárquica (/wiki/)
├── gym/             # Seguimiento de productos · Sistema de mantenimiento tabular
└── prompts/         # Biblioteca de prompts IA · Arquitectura No-DB (GitHub API)
```

### Dual-Stack UI — Nunca mezclar

| Área | CSS | JS | Componentes |
|------|-----|----|-------------|
| Pública (`/`, `/blog/`, `/wiki/`) | Tailwind CDN + Custom CSS | Vanilla ES6+ | `{% load components_ui %}` |
| Privada (`/private/`) | Bootstrap 5.3 | Vanilla ES6+ | `comp_tabla_mantenimiento`, `comp_*` |

---

## Instalación local

### Requisitos
- Python 3.11+
- Git

### Setup

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd porfolio

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con los valores reales

# 5. Base de datos y seed
python manage.py migrate
python manage.py setup_db  # restaura db_backup.json si la BD está vacía

# 6. Servidor de desarrollo
python manage.py runserver
```

### Variables de entorno requeridas

```ini
DJANGO_ENV=development
DEBUG=True
SECRET_KEY=tu-clave-secreta
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=                          # vacío = SQLite en local
RECAPTCHA_PUBLIC_KEY=
RECAPTCHA_PRIVATE_KEY=
GITHUB_TOKEN_COMPONENTES=              # para instalar django-components-ui
```

Ver `.env.example` para la lista completa con descripciones.

---

## Comandos frecuentes

```bash
# Tests
python manage.py test                   # todos los tests
python manage.py test app.blog          # solo una app
python manage.py test --verbosity=2     # con detalle

# Cobertura
coverage run manage.py test
coverage report
coverage html                           # abre htmlcov/index.html

# Linting
ruff check app/ --select F401 --fix    # limpia imports no usados

# Base de datos
python manage.py migrate
python manage.py setup_db              # restaura desde backup si BD vacía
python manage.py setup_db --seed       # fuerza seed con SQL

# Estáticos
python manage.py collectstatic --noinput

# Wiki (documentum)
python manage.py seed_documentum       # importa Markdown desde /docs/
```

También disponible mediante `Makefile`:

```bash
make test       # ejecuta tests
make coverage   # coverage report + HTML
make lint       # ruff check
make run        # servidor de desarrollo
make migrate    # migrate + setup_db
```

---

## Despliegue en Render

### CI/CD
- Push a `main` dispara despliegue automático en Render
- Tests deben pasar localmente antes de mergear

### Comando post-deploy (one-off en Render)

```bash
pip install -r requirements.txt && \
python manage.py migrate && \
python manage.py setup_db \
  --seed \
  --seed-sql documentum_seed_postgres.sql \
  --normalize \
  --render && \
python create_admin.py && \
python manage.py collectstatic --noinput
```

### Variables de entorno en Render

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta Django |
| `DATABASE_URL` | PostgreSQL Supabase (session pooler) |
| `DEBUG` | `False` en producción |
| `ALLOWED_HOSTS` | `hernandezpalo.es` |
| `CSRF_TRUSTED_ORIGINS` | `https://hernandezpalo.es` |
| `RECAPTCHA_PUBLIC_KEY` | Google reCAPTCHA v3 |
| `RECAPTCHA_PRIVATE_KEY` | Google reCAPTCHA v3 |
| `GITHUB_TOKEN_COMPONENTES` | Token para instalar `django-components-ui` |

---

## Resiliencia y Backup

La base de datos en Render (free tier) tiene persistencia limitada.
El proyecto implementa un sistema de backup/restauración automático:

- **Backup**: botón en `/private/` → ejecuta `dumpdata` → `db_backup.json`
- **Restauración automática**: `setup_db` detecta BD vacía y carga `db_backup.json`
- **Regla**: tras modificar modelos de `gym` o `landing`, regenerar `db_backup.json`

---

## SEO y Performance

### Core Web Vitals (desktop, producción)

| Métrica | Valor | Score |
|---------|-------|-------|
| FCP | 0.8s | 96 |
| LCP | 2.2s | 56 (limitado por TTFB del free tier) |
| TBT | 0ms | 100 |
| CLS | ~0.05 | ~90 (fix `font-display: optional`) |
| SI | 2.1s | 57 |

> El TTFB de 1520ms es el principal limitador en el free tier de Render.
> Con Render Starter ($7/mes), el LCP bajaría a ~0.8s.

### Optimizaciones implementadas

- Critical CSS inline (above-the-fold sin bloqueo de render)
- Fuentes self-hosted WOFF2 con `font-display: optional` (elimina CLS)
- Bundle CSS diferido con preload + onload hack
- AOS y Typed.js en local (sin CDN externo, sin SPOF)
- reCAPTCHA cargado con `async` (no es render-blocking)
- Preconnect para GitHub CDN y Google/gstatic
- Imágenes con `loading="lazy" decoding="async"` bajo el fold
- WhiteNoise con cache HTTP 1 año en estáticos
- `django-htmlmin` activo en producción
- Caché de querysets: 30 min para home, 15 min para related posts

---

## Estructura de Tests

```
app/
├── blog/tests.py              # Modelos y vistas del blog (13 tests)
├── documentum/tests.py        # Modelos y seed (4 tests)
├── gym/tests.py               # Modelos y API DRF (23 tests)
├── prompts/tests.py           # Acceso, CRUD y GitHub mock (13 tests)
└── landing/tests/
    ├── test_models.py         # Modelos de landing (13 tests)
    ├── test_views.py          # Vistas home y private (10 tests)
    └── test_setup_db.py       # Comando setup_db (4 tests)
```

**Total: 83 tests — Tiempo de ejecución: < 1s**

---

## Sistema de Mantenimiento Tabular (receta canónica)

Para cualquier CRUD de un modelo en el portal interno:

```
1. serializers.py  → ModelSerializer con fields = '__all__'
2. api.py          → MetadataMixin + ModelViewSet con permission_classes = [IsAuthenticated]
3. views.py        → función con columnas Tabulator + api_url
4. template        → extiende private/layouts/base.html + comp_tabla_mantenimiento
```

Ver `app/gym/` como referencia de implementación completa.

---

## Librería de Componentes

`django-components-ui` — librería privada con **46 componentes**:

- **19 Atomic Elements**: `comp_button`, `comp_input_text`, `comp_modal`, `comp_chart`, `comp_data_card`, `comp_kanban`...
- **27 Complex Components**: `comp_tabla_mantenimiento`, `comp_sidebar_menu`, `comp_agenda`, `comp_timeline`...

```bash
# Instalación desde GitHub
pip install "django-components-ui @ git+https://${GITHUB_TOKEN_COMPONENTES}@github.com/hernandezpalo83/COMPONENTES.git#subdirectory=django_components_ui"

# Modo editable (desarrollo local)
pip install -e /ruta/a/COMPONENTES/django_components_ui/
```

---

## Documentación interna

| Archivo | Propósito |
|---------|-----------|
| `CLAUDE.md` | Guía definitiva para Claude Code — reglas y estándares del proyecto |
| `PUBLIC_AREA.md` | Aislamiento del área pública · Stack canónico · SEO checklist |
| `ROADMAP.md` | Futuras mejoras y funcionalidades planificadas |
| `PRODUCT.md` | Visión estratégica TPM del portfolio |
| `CHANGELOG.md` | Historial de cambios por versión |
| `COMPONENTS_AI_GUIDE.md` | Referencia de `django-components-ui` para desarrollo |

---

## Licencia

Proyecto privado — código propietario de Javier Hernández Martin.
No se permite reproducción, distribución ni uso comercial sin autorización expresa.

---

*Última actualización: 2026-03-22*
