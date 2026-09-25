# 🧩 Guía de Apps — HernandezPalo Portfolio

**Descripción detallada de cada aplicación: responsabilidades, modelos, vistas y patrones específicos.**

---

## `app.landing` — Hub Principal + Portal Privado

### Responsabilidad
- **Pública**: Landing page (`/`) con hero, skills, proyectos, contacto
- **Privada**: Portal interno (`/private/*`) con dashboard, gestión de contenidos

### Modelos
- `LandingData` — Datos del home (secciones dinámicas)
- `Portfolio` — Proyectos mostrados en hero
- `Skills` — Competencias técnicas
- `Projects` — Proyectos detallados
- `ContactMessage` — Mensajes de contacto (formulario)

### Vistas públicas
| Ruta | Función | Template |
|---|---|---|
| `/` | `home()` | `landing/home.html` |
| `/sitemap.xml` | Sitemap dinámico | XML |
| `/robots.txt` | Directivas bots | TXT |

### Vistas privadas (requieren login)
| Ruta | Función | Responsabilidad |
|---|---|---|
| `/private/` | `portal_dashboard()` | Dashboard central |
| `/private/mantenimiento/*` | CRUDs tabulares | Gestión de datos |

### Notas técnicas
- **SEO**: Home tiene schema.org `Person` JSON-LD completo
- **Caché**: `landing_home_data` cachea 30 min
- **Backup**: Modelos aquí persisten en `db_backup.json` para Render

---

## `app.blog` — CMS de Posts

### Responsabilidad
Engine de contenidos con soporte para SEO avanzado, categorías dinámicas y búsqueda.

### Modelos
- `Post` — Posts con autor, fecha, contenido CKEditor5, meta SEO
- `Category` — Categorías de posts
- `Tag` — Tags para clasificación cruzada

### Vistas públicas
| Ruta | Función | Template |
|---|---|---|
| `/blog/` | `post_list()` | `blog/post_list.html` |
| `/blog/<slug>/` | `post_detail()` | `blog/post_detail.html` |

### Notas técnicas
- **SEO**: Cada post tiene meta description + Open Graph + Twitter Card + Schema.org `BlogPosting`
- **Contenido**: CKEditor5 para formato rich text
- **Paginación**: Soporta `rel="prev"` / `rel="next"`
- **Caché**: Posts relacionados cachean 15 min

---

## `app.documentum` — Wiki Técnica

### Responsabilidad
Documentación técnica con navegación jerárquica, búsqueda y estructura de categorías.

### Modelos
- `Document` — Páginas wiki con categoría, nivel jerárquico, contenido CKEditor5
- `Category` — Categorías (Operations, Developer, Architecture, etc.)

### Vistas públicas
| Ruta | Función | Template |
|---|---|---|
| `/wiki/` | `wiki_home()` | `documentum/home.html` |
| `/wiki/<category>/<slug>/` | `wiki_detail()` | `documentum/detail.html` |

### Notas técnicas
- **Sincronización**: Comando `python manage.py seed_documentum` importa desde `docs/` MD
- **Caché**: Navegación cachea 10 min (`docs_navigation_data`)
- **SEO**: URLs amigables + meta per-documento

---

## `app.gym` — Inventario + Mantenimiento Tabular

### Responsabilidad
Módulo de inventario con **sistema de mantenimiento tabular** (patrón canónico para CRUDs).

### Modelos
- `Producto` — Artículos de inventario con estado, categoría, precio
- `Estado` (Choices) — Estados posibles de producto
- `Categoria` (Choices) — Categorías de productos

### Vistas privadas
| Ruta | Función | Responsabilidad |
|---|---|---|
| `/gym/` | `gym_dashboard()` | Dashboard de inventario |
| `/gym/mantenimiento/productos/` | `mantenimiento_productos()` | CRUD tabular vía Tabulator |

### Implementación canónica
Sigue la **Receta de Mantenimiento Tabular** documentada en `1-ARQUITECTURA.md`:
1. Serializer con `fields = '__all__'`
2. ViewSet + MetadataMixin en `api.py`
3. Vista que construye config Tabulator + API URL
4. Plantilla que extiende `private/layouts/base.html` + `comp_tabla_mantenimiento`

### Notas técnicas
- **API**: `/gym/api/producto-api/` (requiere autenticación)
- **Metadatos**: `/gym/api/producto-api/metadata/` expone estructura de campos
- **Persistencia**: Datos de productos persisten en `db_backup.json`

---

## `app.prompts` — Biblioteca IA (No-DB)

### Responsabilidad
Repositorio de prompts de IA. **Arquitectura única sin BD**: sincroniza directamente con GitHub API.

### Estructura
- Prompts almacenados en GitHub repositorio privado
- Sincronización vía GitHub API (requiere `GITHUB_TOKEN_COMPONENTES` en settings)
- Caché local para evitar rate limits

### Vistas públicas
| Ruta | Función | Responsabilidad |
|---|---|---|
| `/prompts/` | `prompts_list()` | Listado de prompts |
| `/prompts/<id>/` | `prompts_detail()` | Detalle de prompt |

### Notas técnicas
- **No-DB**: Ningún modelo en BD, solo lectura de GitHub
- **Token**: `GITHUB_TOKEN_COMPONENTES` en environment vars
- **Caché**: Prompts cachean para evitar rate limits de GitHub

---

## `app.config` — Configuración Central

### Responsabilidad
Configuración global, URLs, logging y WSGI.

### Archivos clave
| Archivo | Responsabilidad |
|---|---|
| `settings.py` | Configuración Django (DB, apps, middleware, logging) |
| `urls.py` | Routing global + dict `sitemaps` para apps públicas |
| `logging_config.py` | Configuración de loggers por app |
| `wsgi.py` | Punto de entrada WSGI para Render |

### Variables de entorno obligatorias
```
SECRET_KEY=<generado>
DATABASE_URL=postgresql://...  # Supabase en prod
DEBUG=False                      # En prod
ALLOWED_HOSTS=hernandezpalo.es,www.hernandezpalo.es
GITHUB_TOKEN_COMPONENTES=<token>
RECAPTCHA_PUBLIC_KEY=<key>
RECAPTCHA_PRIVATE_KEY=<key>
```

---

## 🔄 Flujo de una solicitud típica

```
Solicitud HTTP
    ↓
app.config.urls (routing)
    ↓
app.{landing|blog|documentum|gym|prompts}.views
    ↓
Modelo → clean() → lógica de negocio
    ↓
Template (público o privado)
    ↓
Response HTTP
```

---

## ✅ Checklist al añadir una nueva app

- [ ] Crear app: `python manage.py startapp nueva_app`
- [ ] Registrar en `INSTALLED_APPS` (en `settings.py`)
- [ ] Definir modelos con `__str__`, `Meta.ordering`, `clean()`
- [ ] Si es pública: registrar en dict `sitemaps` de `urls.py`
- [ ] Si tiene vistas públicas: añadir meta tags SEO + sitemap
- [ ] Si tiene datos: setup en `setup_db` para backup/restore
- [ ] Documentar en este archivo (sección propia)

