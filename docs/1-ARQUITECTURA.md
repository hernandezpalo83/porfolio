# 🏗️ Arquitectura — HernandezPalo Portfolio

**Visión global del sistema, stack técnico, estructura de apps y patrones canónicos de implementación.**

---

## 1. Visión y Propósito

Portfolio profesional de **Javier Hernández Martin** diseñado como **CMS Técnico Escalable** bajo estándares **TPM (Technical Product Management)**. Enfoque en resiliencia, performance extrema y automatización.

### Valores del proyecto
- **Resiliencia**: Backup automático, disaster recovery en Render
- **Performance**: Vanilla JS en público, minificación en prod
- **SEO-first**: Cada página pública registrada en sitemap
- **Escalabilidad**: APIs privadas + portal interno para mantenimiento

---

## 2. Stack técnico

| Capa | Tecnología | Detalles |
|---|---|---|
| **Backend** | Django 5.1+ / Python 3.11+ | Sin DRF para vistas públicas |
| **API (privada)** | Django REST Framework | Endpoints `/*/api/` solo para mantenimiento |
| **DB (prod)** | PostgreSQL — Supabase | Session pooler + SSL |
| **DB (local/test)** | SQLite | Auto-detectado si no hay `DATABASE_URL` |
| **Frontend público** | Vanilla JS ES6+, Custom CSS (Kards), `components_ui` | Zero jQuery |
| **Frontend privado** | Bootstrap 5.3 + Bootstrap Icons + Glassmorphism | `.card-gemini` |
| **Componentes UI** | `django-components-ui` (privada en GitHub) | 52 componentes disponibles |
| **Tablas** | Tabulator JS 6.2.1 | Solo área privada (`comp_tabla_mantenimiento`) |
| **Rich Text** | CKEditor 5 | En `landing`, `blog`, `documentum` |
| **Estáticos** | WhiteNoise + `CompressedManifestStaticFilesStorage` | Cache 1 año |
| **Minificación** | `django-htmlmin` | Producción (`HTML_MINIFY = not DEBUG`) |
| **Deploy** | Render (Web Service) + CI/CD desde `main` | |
| **CDN Assets** | `https://raw.githubusercontent.com/hernandezpalo83/cdn/main` | `BRAND_ASSETS_URL` |

---

## 3. Estructura de aplicaciones

```
app/
├── config/          → settings, urls, logging, wsgi
├── landing/         → Hub principal + Portal privado (/private/)
├── blog/            → CMS de posts + SEO por post
├── documentum/      → Wiki técnica con navegación jerárquica (/wiki/)
├── gym/             → Inventario/Productos + Sistema mantenimiento tabular
└── prompts/         → Biblioteca IA (No-DB, sincroniza con GitHub API)
```

### Responsabilidades por app

| App | Rutas | Modelos | Responsabilidad |
|---|---|---|---|
| `landing` | `/`, `/private/*` | `LandingData`, `Portfolio`, `Skills`, `Projects` | Home pública + Portal interno |
| `blog` | `/blog/`, `/blog/<slug>/` | `Post`, `Category`, `Tag` | CMS de posts + SEO |
| `documentum` | `/wiki/` | `Document`, `Category` | Wiki técnica con navegación jerárquica |
| `gym` | `/gym/`, `/gym/mantenimiento/*` | `Producto`, `Estado`, `Categoria` | Inventario + tablas de mantenimiento |
| `prompts` | `/prompts/` | (No-DB) | Biblioteca IA, sincroniza con GitHub |
| `config` | N/A | N/A | Configuración central |

---

## 4. Dual-Stack UI — NUNCA MEZCLAR

### A. Área Pública (`/`, `/blog/`, `/wiki/`)
- **CSS**: Tailwind CSS (CDN en dev, nunca en prod sin build)
- **Componentes**: `{% load components_ui %}` + tags `comp_*`
- **Iconos**: Heroicons v2 (`HomeIcon`, `CheckIcon`)
- **JS**: Vanilla ES6+, cero jQuery
- **Regla**: Performance extrema, cero dependencias pesadas

### B. Área Privada (`/private/`)
- **CSS**: Bootstrap 5.3 + `private_portal.css`
- **Estética**: Glassmorphism → clase `.card-gemini`, `.rounded-pill`
- **Iconos**: Bootstrap Icons (`bi-shield-lock-fill`, `bi-box-arrow-up-right`)
- **Tablas**: Tabulator JS vía `comp_tabla_mantenimiento`
- **Regla**: Utilidad y gestión de datos eficiente

**Consecuencia de mezclar**: doble carga de CSS, conflictos de estilos, pérdida de performance.

---

## 5. Patrones canónicos

### 5.1 Patrón de Vistas

**Vistas simples**: Funciones con type hints

```python
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def mi_vista(request: HttpRequest) -> HttpResponse:
    contexto = {
        "titulo": "Mi Vista",
        "datos": MiModelo.objects.all()
    }
    return render(request, "mi_app/mi_template.html", contexto)
```

**Regla**: Lógica de negocio va en `clean()` del modelo, **nunca** en la vista.

### 5.2 Modelos — Convenciones obligatorias

```python
from django.db import models
from django.core.exceptions import ValidationError

class MiModelo(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=20,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Mi Modelo"
        verbose_name_plural = "Mis Modelos"
    
    def __str__(self):
        return f"{self.nombre} ({self.estado})"
    
    def clean(self):
        if self.nombre.strip() == "":
            raise ValidationError("El nombre no puede estar vacío")
```

**Obligatorio**:
- `__str__` siempre implementado
- `Meta.ordering` siempre definido
- Validación en `clean()`, **nunca** en la vista
- Idioma: español en `gym`/`landing`, inglés en `blog`

### 5.3 Sistema de Mantenimiento Tabular (Receta Canónica)

Para **cualquier CRUD rápido** de un modelo en el portal interno:

**1. Serializer (`serializers.py`)**:
```python
from rest_framework import serializers
from .models import MiModelo

class MiModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiModelo
        fields = '__all__'
```

**2. ViewSet (`api.py`)**:
```python
from rest_framework import viewsets
from .serializers import MiModeloSerializer

class MiModeloViewSet(viewsets.ModelViewSet):
    queryset = MiModelo.objects.all()
    serializer_class = MiModeloSerializer
```

**3. Vista (`views.py`)**:
```python
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

**4. Plantilla**:
```django
{% extends 'private/layouts/base.html' %}
{% load components_ui %}
{% block content %}
    <div class="card card-gemini shadow-sm p-4">
        {% comp_tabla_mantenimiento data_url=api_url columns=cols searchable=True filterable=True %}
    </div>
{% endblock %}
```

### 5.4 API (DRF) — Solo para mantenimiento interno

- Un `ViewSet` por modelo
- Mixin `MetadataMixin` en `api.py` expone `/metadata/` para descubrir campos
- Serializers con `fields = '__all__'` como default
- Endpoints: `/<app>/api/<modelo>-api/`

---

## 6. SEO — Obligatorio en vistas públicas

Cada vista pública **debe** tener:
- `<title>` descriptivo
- `<meta name="description">` ≤160 chars
- Open Graph tags (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`)
- Twitter Card tags
- Schema.org JSON-LD cuando aplique
- Canonical URL
- Registro en sitemap (`app/config/urls.py` → dict `sitemaps`)

---

## 7. Resiliencia y Backup (Crítico para Render)

BD de Render (free tier) = persistencia limitada. Implementamos:

- **Backup manual**: Botón en `/private/` → ejecuta `dumpdata` a `db_backup.json`
- **Restauración automática**: `python manage.py setup_db` detecta BD vacía y carga `db_backup.json`
- **Seed completo**: `python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render`

**Regla crítica**: Al modificar modelos de `gym` o `landing`, recordar que los datos persisten vía `db_backup.json`. Avisar si un cambio de schema puede romper la restauración.

---

## 8. Logging — NUNCA print()

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detalle técnico")
logger.info("Evento de negocio")
logger.warning("Situación inesperada pero recuperable")
logger.error("Fallo que requiere atención", exc_info=True)
```

- Configuración centralizada: `app/config/logging_config.py`
- Handlers: console (dev) + RotatingFileHandler a `app/logs/django.log` (prod)
- Loggers por app: `app.landing`, `app.blog`, `app.gym`, `app.prompts`

---

## 9. Librería `django-components-ui`

**Instalación**:
```bash
pip install git+ssh://git@github.com/tu-usuario/tu-repo.git#subdirectory=django_components_ui
```

**Componentes clave**:
- `comp_tabla_mantenimiento` — CRUD tabular (Tabulator)
- `comp_tabla` — Lectura de datos
- `comp_button`, `comp_card`, `comp_title`, `comp_badge`, `comp_icon`
- `comp_tabs`, `comp_acordeon`, `comp_steps`, `comp_breadcrumbs`

**Regla**: Usa siempre estos tags en lugar de HTML/Tailwind manual para elementos comunes.

---

## 10. Anti-Patterns — PROHIBIDO

| Anti-Pattern | Motivo |
|---|---|
| Usar `print()` en lugar de `logging` | Logs no estructurados |
| Mezclar Bootstrap y Tailwind | Conflictos, doble carga CSS |
| Vistas públicas sin SEO | Perjudica indexación |
| Lógica de negocio en vistas | Debe ir en `clean()` del modelo |
| Usar jQuery en público | Viola performance extrema |
| Hardcodear URLs de CDN | Usar `BRAND_ASSETS_URL` de settings |
| Tailwind CDN en producción | Warning en consola |
| Modelos sin `__str__`, `Meta.ordering`, `clean()` | Incoherencia |
| sourceMappingURL sin .map | Rompe `collectstatic` en Render |

---

## 11. Cómo evoluciona esta arquitectura

Este documento es **vivo**. Tras cada tarea completada o corrección del usuario:
- ¿Detectaste un patrón de error? → Añádelo como Anti-Pattern
- ¿Cambió una librería o patrón? → Actualiza Tech Stack
- ¿Nueva app? → Documenta en sección 3
- ¿Error recurrente? → Crea regla de oro

**Responsable**: Mantener este documento sincronizado con la realidad del código.

