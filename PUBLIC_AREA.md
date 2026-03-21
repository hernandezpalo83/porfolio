# Área Pública — Guía de Aislamiento y Estándares

> Documento de referencia para mantener el área pública (landing + blog) aislada, optimizada y sin interferencias del back-office.

---

## 1. Qué es el área pública

Rutas públicas (sin autenticación requerida):
- `/` — Landing page principal
- `/blog/` — Listado de posts
- `/blog/<slug>/` — Detalle de post
- `/sitemap.xml` — Sitemap para crawlers
- `/robots.txt` — Directivas para bots
- `/health/` — Health check (Render/Fly.io)

Rutas que **NO son** área pública aunque sean accesibles:
- `/wiki/` — Documentum (área semi-pública, contenido técnico)
- `/login/`, `/logout/` — Auth
- `/admin/`, `/gym/`, `/prompts/`, `/private/` — Back-office

---

## 2. Reglas de aislamiento (NO romper)

### 2.1 CSS / JS
| Regla | Motivo |
|---|---|
| Nunca usar Bootstrap 5 en templates públicos | Bootstrap es solo para `/private/`. Causa conflictos de estilos y doble carga |
| Nunca usar jQuery en el área pública | Viola el principio de performance. Todo debe ser Vanilla JS ES6+ |
| Nunca cargar vendors de CDN externo | SPOF si CDN falla. Typed.js y AOS ya están locales en `static/landing/js/vendor/` y `static/landing/css/vendor/` |
| No añadir `{% load crispy_forms_tags %}` en templates públicos | Carga assets de Bootstrap |

### 2.2 Context Processors
Los context processors corren en **cada request** del área pública. Los actuales son seguros:

| Processor | En público | Coste |
|---|---|---|
| `brand_assets` | Siempre | Solo variables de settings (0 queries) |
| `menu_int_processor` | Retorna `{}` si no autenticado | 0 queries para usuarios anónimos |
| `docs_navigation` | Retorna `{}` si path no empieza por `/wiki/` | 0 queries en landing/blog |

**Regla**: si añades un nuevo context processor, asegúrate de que tenga un guard de path o de autenticación para no ejecutarse en el área pública.

### 2.3 Formularios
- El formulario de contacto (`FormularioContacto`) usa `form.media` → inyecta el script de reCAPTCHA v3
- Este `form.media` solo existe en el contexto de `home()`, no en otras vistas públicas
- `{% if form.media %}{{ form.media }}{% endif %}` en `base.html` es seguro — no carga nada en blog/wiki

### 2.4 DRF / APIs
- Los endpoints `/gym/api/` requieren autenticación (`IsAuthenticated`)
- No exponer endpoints DRF sin autenticación desde el área pública
- El área pública nunca debe depender de la API interna

---

## 3. Stack técnico del área pública (canónico)

```
Templates: app/templates/landing/layouts/base.html (layout base)
           app/templates/landing/components/*.html (componentes)
           app/blog/templates/blog/*.html (templates del blog)

CSS:       landing/css/bundle.v2.css       (CSS consolidado, diferido)
           landing/css/vendor/aos.min.css  (AOS animations, local)
           landing/css/font-awesome/       (iconos, local)
           landing/css/micons/             (iconos adicionales, local)
           Inline critical CSS via: landing/components/critical_css.html

JS:        landing/js/main.js              (lógica principal, defer)
           landing/js/metrics.js           (animaciones SVG + contadores, defer)
           landing/js/vendor/typed.min.js  (typing effect, local)
           landing/js/vendor/aos.min.js    (scroll animations, local)
           blog/js/*.js                    (si se añaden scripts específicos del blog)

Fonts:     landing/fonts/poppins/          (self-hosted WOFF2)
           landing/fonts/lora/             (self-hosted WOFF2)
```

---

## 4. SEO — Checklist por tipo de página

### Landing page (`/`)
- [x] `<title>` con nombre completo + cargo + ciudad
- [x] `<meta description>` ≤160 chars con keywords principales
- [x] Open Graph: `og:title`, `og:description`, `og:image`, `og:url`, `og:type=website`
- [x] Twitter Card: `twitter:card=summary_large_image`, `twitter:title`, `twitter:description`, `twitter:image`
- [x] Schema.org `Person` JSON-LD
- [x] Canonical URL
- [x] Imagen OG en WebP (`og-image.webp`)
- [x] Sitemap registrado en `config/urls.py`

### Post de blog (`/blog/<slug>/`)
- [x] `<title>` = título del post
- [x] `<meta description>` = `meta_description` del post (admin lo rellena)
- [x] Open Graph `og:type=article`
- [x] Twitter Card con imagen del post
- [x] Schema.org `BlogPosting` JSON-LD completo
- [x] Canonical con URL absoluta
- [x] `rel="prev"` / `rel="next"` en la paginación del listado

### Listado del blog (`/blog/`)
- [x] Meta description dinámica según filtro activo (búsqueda / categoría / año / por defecto)
- [x] `rel="prev"` / `rel="next"` para paginación
- [x] Twitter Card con título y descripción del blog
- [ ] **TODO**: Sitemap de categorías de blog

---

## 5. Performance — Estrategias implementadas

### Critical Rendering Path
1. **Critical CSS inline** → `landing/components/critical_css.html` inlineado en `<head>`
   → Asegura FCP (First Contentful Paint) sin bloqueo de render
2. **Bundle CSS diferido** → `rel="preload"` + `onload` hack + `<noscript>` fallback
3. **Fonts preloadadas** → `rel="preload" as="font"` para Poppins y Lora
4. **Hero image preloadada** → `rel="preload" as="image"` para `intro-bg.webp`

### Lazy Loading
- Todas las imágenes bajo el fold: `loading="lazy" decoding="async"`
- Hero y primera imagen de perfil: `loading="eager"` (son LCP)

### Caching
| Dato | Cache key | TTL |
|---|---|---|
| Datos landing (skills, projects, etc.) | `landing_home_data` | 30 min |
| Posts relacionados por categoría | `related_posts_{category_id}` | 15 min |
| Menú interno por usuario | `menu_items_user_{id}` | 60 min |
| Navegación wiki | `docs_navigation_data` | 10 min |
| Estáticos (WhiteNoise) | HTTP Cache-Control | 1 año |

### Vendors locales (sin CDN externo)
- `typed.min.js` → `static/landing/js/vendor/typed.min.js` (v2.1.0, 9KB)
- `aos.min.js` → `static/landing/js/vendor/aos.min.js` (v2.3.1, 14KB)
- `aos.min.css` → `static/landing/css/vendor/aos.min.css` (v2.3.1, 25KB)

---

## 6. Seguridad del área pública

| Medida | Implementación |
|---|---|
| CSRF | `CsrfViewMiddleware` activo globalmente |
| reCAPTCHA v3 | `ReCaptchaField(widget=ReCaptchaV3)` en `FormularioContacto` |
| Honeypot | Campo `website` oculto en `FormularioContacto` — los bots lo rellenan |
| Rate limiting | `@ratelimit(key='ip', rate='5/h', method='POST')` en `home()` |
| HTTPS + HSTS | Solo en producción (`DEBUG=False`) |
| XSS en contenido CKEditor | `\|safe` solo en contenido de CKEditor5, que sanitiza el output |
| SQL injection | ORM Django — nunca raw SQL en vistas públicas |

---

## 7. Qué NO hacer en el área pública

```
❌ Añadir {% load crispy_forms_tags %} en templates de landing/blog
❌ Importar Bootstrap CSS/JS en base.html (solo en private/layouts/base.html)
❌ Usar jQuery ($) en scripts del área pública
❌ Cargar scripts de CDN externo sin fallback local
❌ Crear vistas públicas sin meta description ni canonical
❌ Añadir endpoints DRF sin autenticación accesibles desde URLs públicas
❌ Usar print() en lugar de logging.getLogger(__name__)
❌ Hardcodear URLs de assets (usar BRAND_ASSETS_URL de settings)
❌ Registrar un context processor que haga queries en todas las páginas públicas
❌ Añadir dependencias de npm/node sin documentar el build step
```

---

## 8. Cómo añadir una nueva sección pública

1. **Modelo** → en `app/landing/models.py` (o `app/blog/`) con `clean()`, `Meta.ordering`, `__str__`
2. **Vista** → añadir al dict de `home_data` en `landing/views.py::home()` para que se incluya en la caché
3. **Template** → nuevo componente en `app/templates/landing/components/<nombre>.html`
4. **Incluir** en `home.html`: `{% include "landing/components/<nombre>.html" %}`
5. **SEO** → si tiene URLs propias, registrar sitemap en `app/config/urls.py`
6. **Caché** → si los datos cambian raramente, añadir al bloque de `home_data` (30 min TTL)
7. **Tests** → añadir al test `test_home_context_has_required_keys` en `landing/tests/test_views.py`
8. **Invalidar caché** → si el admin modifica los datos, llamar `cache.delete('landing_home_data')` en el signal o `save()` del modelo

---

## 9. Actualizar los vendors locales

Si Typed.js o AOS sacan una nueva versión:

```bash
# Actualizar typed.js
curl -sL "https://unpkg.com/typed.js@X.Y.Z/dist/typed.umd.js" \
  -o app/landing/static/landing/js/vendor/typed.min.js

# Actualizar AOS
curl -sL "https://unpkg.com/aos@X.Y.Z/dist/aos.js" \
  -o app/landing/static/landing/js/vendor/aos.min.js
curl -sL "https://unpkg.com/aos@X.Y.Z/dist/aos.css" \
  -o app/landing/static/landing/css/vendor/aos.min.css
```

Versiones actuales: Typed.js **2.1.0** · AOS **2.3.1**
