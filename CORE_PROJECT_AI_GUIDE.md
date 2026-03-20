# 🧠 Master Guide: HernandezPalo Portfolio AI & Development

Este documento es la referencia definitiva para el desarrollo, mantenimiento y evolución del ecosistema **HernandezPalo Portfolio**. Proporciona el contexto arquitectónico, los estándares de diseño y las reglas de implementación para que cualquier IA (o desarrollador) mantenga la coherencia del sistema.

---

## 🏗️ 1. Visión y Arquitectura Core

El proyecto es un **CMS Técnico Escalable** basado en **Django 5.x**, diseñado bajo el estándar **TPM (Technical Product Management)**. Pone foco en la resiliencia, el rendimiento extremo y la automatización.

### 📁 Estructura de Aplicaciones
- **`app.landing`**: Hub principal. Gestiona la página de inicio, el SEO global y el **Portal Interno (Área Privada)**.
- **`app.blog`**: Engine de contenidos con soporte para SEO avanzado y categorías dinámicas.
- **`app.documentum` (Wiki)**: Gestión de documentación técnica y guías con navegación jerárquica.
- **`app.prompts`**: Biblioteca de assets de IA. **Arquitectura No-DB**: Los datos se sincronizan directamente con un repositorio de GitHub mediante API (JSON).
- **`app.gym`**: Módulo dedicado a seguimiento y lógica para gimnasios e inventario (Productos). Incluye el sistema de mantenimiento tabular.
- **`app.config`**: Configuración central de Django (`settings.py`, `urls.py`).

---

## 🎨 2. Estándares de UI (Dual-Stack System)

Este proyecto utiliza dos sistemas de UI coexistentes dependiendo del contexto. **NO MEZCLARLOS**.

### A. Área Pública (Landing/Blog/Wiki)
- **Framework**: Tailwind CSS.
- **Componentes**: Librería propia `components_ui` (vía `inclusion_tags`).
- **Iconos**: Heroicons v2 (ej. `CheckIcon`, `HomeIcon`).
- **Referencia**: `COMPONENTS_AI_GUIDE.md`.

### B. Portal Interno / Páginas Privadas (`/private/`)
- **Framework**: Bootstrap 5.3 + Custom CSS (`private_portal.css`).
- **Estética**: Glassmorphism (clase `.card-gemini`), sombras suaves y bordes redondeados (`rounded-pill`, `rounded-4`).
- **Iconos**: Bootstrap Icons (`bi-box-arrow-up-right`, `bi-shield-lock-fill`).
- **Tablas**: Tabulator JS integrado en `components_ui`.
- **Regla**: El área privada prioriza la utilidad y la gestión de datos eficiente.

---

## 🔧 3. Procesos Críticos y Resiliencia (TPM Strategy)

### 📂 Sistema de Backup y Disaster Recovery
El proyecto incluye un mecanismo de persistencia para entornos con base de datos volátil (como el nivel gratuito de Render):
- **Backup Manual**: En el Dashboard `/private/`, el botón "Generar Backup" ejecuta `dumpdata` sobre `landing` y `gym` hacia `db_backup.json`.
- **Restauración Automática**: El comando `python manage.py setup_db` detecta si la BD está vacía y carga automáticamente el último `db_backup.json`.
- **Seed de Datos**: `setup_db --seed` también inyecta contenido inicial para la Wiki (`app.documentum`) desde archivos SQL.

### 📊 Sistema de Mantenimiento Simple (Tabular)
Para gestionar cualquier tabla del sistema de forma rápida (CRUD completo), se utiliza el componente `comp_tabla_mantenimiento` basado en **Tabulator JS**.

**Receta de Implementación:**

1. **Serializer (serializers.py)**:
   ```python
   from rest_framework import serializers
   from .models import MiModelo
   class MiModeloSerializer(serializers.ModelSerializer):
       class Meta:
           model = MiModelo
           fields = '__all__'
   ```

2. **ViewSet (api.py)**:
   ```python
   from rest_framework import viewsets
   from .serializers import MiModeloSerializer
   class MiModeloViewSet(viewsets.ModelViewSet):
       queryset = MiModelo.objects.all()
       serializer_class = MiModeloSerializer
   ```

3. **Vista de Mantenimiento (views.py)**:
   ```python
   def mantenimiento_modelo(request):
       columnas = [
           {"title": "ID", "field": "id", "width": 70},
           {"title": "Nombre", "field": "nombre", "headerFilter": "input"},
           # ... más columnas según Tabulator JS
       ]
       return render(request, "tu_app/mantenimiento.html", {
           "cols": columnas,
           "api_url": "/tu_app/api/modelo-api/"
       })
   ```

### 📊 Sistema de Mantenimiento Simple (Tabular)
...
4. **Plantilla (tu_app/mantenimiento.html)**:
   ```django
   {% extends 'private/layouts/base.html' %}
   {% load components_ui %}
   {% block content %}
       <div class="card card-gemini shadow-sm p-6">
           {% comp_tabla_mantenimiento data_url=api_url columns=cols searchable=True filterable=True %}
       </div>
   {% endblock %}
   ```

> [!WARNING]
> **Troubleshooting**: Si obtienes `TemplateDoesNotExist` o `Invalid filter 'to_json'`, asegúrate de que la app `components_ui` esté copiada localmente en `app/components_ui` y que `INSTALLED_APPS` use `'app.components_ui'`. Consulta `COMPONENTS_AI_GUIDE.md` para más detalles.

---

## 🔍 4. Estándares SEO y Performance

- **Metadatos**: Cada página debe definir Título, Descripción y etiquetas Open Graph.
- **Sitemaps**: Nuevas apps con contenido público deben registrarse en `app/config/urls.py` dentro del diccionario `sitemaps`.
- **Rendimiento**:
  - Evitar librerías pesadas en el área pública.
  - Usar `webp` para imágenes (ver `PERSONAL_BRAND` en settings).
  - Mantener `htmlmin` activo para reducir el peso del DOM.

---

## 🔐 5. El Área Privada (Interno)

El portal interno es el corazón operativo del proyecto.
- **Path**: `/private/` (login requerido).
- **Layout**: `private/layouts/base.html` (usa Sidebar + Navbar colapsable).
- **Funcionalidades Críticas**:
  - **Backups**: Botón de exportación a `db_backup.json` en el Dashboard.
  - **Prompt Engineering**: Repositorio de prompts en `app.prompts`.
  - **Mantenimiento**: Tablas dinámicas (Tabulator) para gestión rápida de modelos (ej. Productos en `/gym/mantenimiento/`).

---

## 🤖 5. Reglas de Oro para la IA

Cuando trabajes en este proyecto, sigue estas directrices estrictas:

1. **Contexto de UI**: Si editas algo en `app/templates/private/`, usa **Bootstrap 5**. Si es en `app/templates/landing/` (público), usa **Tailwind + components_ui**.
2. **Resiliencia de Datos**: Cada vez que modifiques modelos en `gym` o `landing`, recuerda que los datos se persisten vía `db_backup.json` en entornos de despliegue limitado (Render).
3. **SEO**: Nunca crees una vista pública sin su correspondiente `sitemap` y etiquetas meta.
4. **Nomenclatura**: Las vistas internas deben seguir el patrón `nombre_app:private_view`.
5. **No Placeholders**: Usa imágenes reales desde el CDN de `PERSONAL_BRAND` o genera assets funcionales.

---

> [!IMPORTANT]
> Esta guía se complementa con `COMPONENTS_AI_GUIDE.md`. Siempre consulta ambos archivos antes de proponer cambios estructurales o visuales.
