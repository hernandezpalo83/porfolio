# ROADMAP — HernandezPalo Portfolio
> Registro vivo de ideas, mejoras y funcionalidades. Ordenado por estado y prioridad.
> Última revisión: **2026-03-22**

---

## Estado del proyecto

| Área | Estado |
|------|--------|
| Tests | 83 · 100% pass |
| Lighthouse Mobile | ~85 |
| Lighthouse Desktop | ~82 (TTFB cold start free tier) |
| CLS | ~0.05 |
| CI/CD | GitHub Actions activo (Develop + main) |
| django-components-ui | v1.1.0 · 46 componentes |

---

## ✅ Completado recientemente

| ID | Descripción | Fecha |
|----|-------------|-------|
| FEAT-003 | Cache invalidation signals para modelos landing | 2026-03-22 |
| TECH-001 | Sitemap de categorías del blog (`BlogCategorySitemap`) | 2026-03-22 |
| TECH-002 | `width`/`height` explícitos en imagen de perfil (CLS fix) | 2026-03-22 |
| TECH-003 | CSP en modo Report-Only (`django-csp`, endpoint `/csp-report/`) | 2026-03-22 |
| TECH-006 | Sentry SDK integrado en producción (activable con `SENTRY_DSN`) | 2026-03-22 |
| TECH-007 | GitHub Actions CI: tests + ruff en cada PR a `main` | 2026-03-22 |
| TECH-008 | RSS Feed del blog (`/blog/feed/` RSS 2.0 + `/blog/feed/atom/` Atom) | 2026-03-22 |
| TECH-009 | Cache invalidation signals para `blog.Post` | 2026-03-22 |
| VIS-002 | Animación del timeline: línea que se dibuja al hacer scroll | 2026-03-22 |
| VIS-003 | Gradiente animado en la sección hero | 2026-03-22 |
| VIS-004 | Project Showcase: tech-tags, estado, overlay, tarjeta destacada | 2026-03-22 |
| PERF-001 | `font-display: optional` en Poppins, Lora, FontAwesome, micons | 2026-03-22 |
| PERF-002 | reCAPTCHA script con `async` (override template `js_v3.html`) | 2026-03-22 |
| PERF-003 | AOS CSS movido al `<head>` con preload diferido | 2026-03-22 |
| PERF-004 | Preconnect para Google, gstatic | 2026-03-22 |
| PERF-005 | Carrusel 3D: efecto profundidad con `requestAnimationFrame` | 2026-03-22 |
| SEC-001 | `IsAuthenticated` en todos los ViewSets DRF | 2026-03-21 |
| SEC-002 | Honeypot + ratelimit (5/h) en formulario de contacto | 2026-03-21 |
| SEO-001 | Blog category sitemap + `rel=prev/next` en paginación | 2026-03-21 |
| SEO-002 | Twitter Cards completas con defaults en base.html | 2026-03-21 |
| NEW-003 | Newsletter con double opt-in: modelo `Subscriber`, admin, sidebar widget | 2026-03-22 |
| NEW-004 | Búsqueda full-text: `SearchVector`/`SearchQuery` (Postgres) + fallback SQLite | 2026-03-22 |

---

## 🔥 Prioridad Alta

### FEAT-001 · Sección "Recetas" en el portal privado
**Descripción:** Apartado en `/private/` con plantillas de código funcional y copiable.

Recetas planificadas:
- `recipe-login` — Login Django (`AuthenticationForm`, CSRF, mensajes, redirección)
- `recipe-crud` — CRUD completo: listado Tabulator + formulario alta + confirmación borrado
- `recipe-app-starter` — Plantilla base: navbar + sidebar + layout inicial para nueva app

**Valor:** Referencia interna. Acelera el bootstrapping de nuevos proyectos Django.
**Complejidad:** Media · 1-2 sesiones

---

### FEAT-002 · Nuevos componentes en `django-components-ui`
**Descripción:** Componentes detectados como necesarios en el uso real:

| Componente | Descripción |
|------------|-------------|
| `comp_login_form` | Formulario de login completo (CSRF, errores, remember me) |
| `comp_empty_state` | Estado vacío con icono, título, descripción y CTA |
| `comp_stat_grid` | Grid responsive de KPI cards |
| `comp_search_bar` | Barra de búsqueda standalone con debounce |
| `comp_confirm_action` | Confirmación de acción destructiva inline |
| `comp_copy_button` | Botón copiar al portapapeles con feedback |

**Complejidad:** Media · 2-3 sesiones

---

### FEAT-004 · Upgrade Render a paid tier
**Descripción:** El TTFB actual en producción es ~1500ms (cold start del free tier).
Render Starter ($7/mes) mantiene el servidor caliente → TTFB < 200ms.

**Impacto Lighthouse Desktop:** +15-20 puntos (LCP 2.2s → ~0.8s → score 95+)
**Acción:** Cambio de plan en el dashboard de Render. No requiere código.

---

## 🛠️ Mejoras Técnicas

### TECH-003 · CSP — Pasar a modo Enforce
**Estado:** Report-Only activo. Las violaciones se reciben en `/csp-report/`.
**Proceso restante:**
1. Recoger violaciones en producción durante 1-2 semanas
2. Refinar la política hasta que esté limpia
3. Cambiar `CONTENT_SECURITY_POLICY_REPORT_ONLY` → `CONTENT_SECURITY_POLICY` en `base.py`

**Riesgo:** Medio. El paso de Report-Only a Enforce puede romper features si quedan violaciones.
**Complejidad:** Baja (ya implementado Report-Only) · 1 sesión de ajuste

---

### TECH-004 · Tests E2E con Playwright
**Descripción:** Complementar los 83 tests unitarios con tests de browser:

```bash
pip install playwright
playwright install chromium
```

Tests planificados:
- Navegación completa de la landing page (scroll, AOS, carrusel)
- Relleno y envío del formulario de contacto (mock reCAPTCHA)
- Listado del blog + filtro por categoría
- Detalle de post

**Valor:** Detectar regresiones visuales antes de cada deploy.
**Complejidad:** Media · 2 sesiones

---

### TECH-005 · Tailwind CSS build local
**Descripción:** Sustituir el CDN de Tailwind por un build con PurgeCSS.

```bash
npm init -y && npm install -D tailwindcss
npx tailwindcss -o app/landing/static/landing/css/tailwind.output.css --minify
```

**Ahorro:** ~340KB de CSS sin usar eliminados. Sin warning de CDN en consola.
**Complejidad:** Alta (requiere step en CI/CD y en Render) · 1 sesión + configuración

---

### TECH-006 · Sentry — Activar en Render
**Estado:** Código integrado. Solo falta añadir la variable de entorno.
**Acción:** Dashboard Render → Environment → `SENTRY_DSN = <dsn del proyecto>`
**Coste:** Free tier de Sentry cubre el volumen de este proyecto.

---

### NEW-003 · Newsletter — Conectar email backend
**Estado:** Modelo `Subscriber`, double opt-in, admin y widget del sidebar implementados.
**Pendiente:** Conectar un backend de email para enviar la confirmación.

```python
# settings/production.py — añadir cuando se tenga cuenta SendGrid
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = env('SENDGRID_API_KEY')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@hernandezpalo.es'
```

**Variable nueva en Render:** `SENDGRID_API_KEY`
**Complejidad:** Baja · 30 min (ya tiene el TODO en `views.py`)

---

## ✨ Nuevas Funcionalidades

### NEW-002 · Modo oscuro
**Descripción:** Dark mode toggle persistido en `localStorage`.

**Reto principal:** El CSS heredado (Kards) no usa custom properties.
Requiere refactorizar variables CSS o añadir capa de override.

**Enfoque recomendado:**
1. Definir `--color-bg`, `--color-text`, `--color-accent` en `:root`
2. Clase `[data-theme="dark"]` en `<html>` con overrides
3. Toggle button en navbar con icono luna/sol

**Complejidad:** Alta · 3-4 sesiones

---

### NEW-005 · Analítica de visitas (Privacy-first)
**Descripción:** Integrar analítica sin cookies y sin banner de consentimiento.

Opciones:
| Herramienta | Precio | Hosting |
|-------------|--------|---------|
| **Umami** | Gratis | Self-hosted (Railway) |
| **Plausible** | $9/mes | Cloud |
| **Fathom** | $14/mes | Cloud |

**Valor:** Datos reales de audiencia (páginas vistas, posts más leídos, países, fuentes de tráfico).
**Complejidad:** Baja · 1h

---

### NEW-006 · Internacionalización (i18n) — versión en inglés
**Descripción:** Doble idioma (ES/EN) en la landing y el blog.

**Proceso:**
1. `django.middleware.locale.LocaleMiddleware`
2. `USE_I18N = True`, `LANGUAGE_CODE = 'es'`
3. `makemessages -l en` + traducciones
4. URLs: `/es/` y `/en/` con `i18n_patterns`

**Reto:** Textos hardcodeados en templates y en datos del admin.
**Valor:** Ampliar audiencia al mercado anglosajón. Muy relevante para TPM internacional.
**Complejidad:** Alta · 5-7 sesiones

---

### NEW-007 · Testimonios / Recomendaciones de LinkedIn
**Descripción:** Sección en la landing con recomendaciones de colegas.

Modelo:
```python
class Testimonio(models.Model):
    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=150)
    empresa = models.CharField(max_length=100)
    foto = models.CharField(max_length=500, blank=True)
    texto = models.TextField()
    linkedin_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
```

**Complejidad:** Baja · 1 sesión (modelo + template + admin)

---

## 🎨 Mejoras Visuales

### VIS-001 · Animación del número en métricas
**Estado:** Ya implementado (IntersectionObserver + `requestAnimationFrame` con ease-out cuadrático).

### VIS-005 · Lazy loading de secciones completas
**Descripción:** Usar `IntersectionObserver` para diferir la carga de secciones pesadas
(carrusel de empresas, métricas) hasta que el usuario haga scroll hasta ellas.

**Valor:** Mejora LCP y el tiempo hasta interactividad en conexiones lentas.
**Complejidad:** Baja · 1h

---

### VIS-006 · Micro-interacciones en el navbar
**Descripción:** Indicador activo animado en el navbar que "desliza" hacia el ítem actual.
Similar al tab indicator de Material Design, implementado con CSS y ResizeObserver.

**Complejidad:** Media · 1 sesión

---

## 📊 Métricas y objetivos

| Métrica | Actual (est.) | Objetivo |
|---------|--------------|----------|
| Lighthouse Mobile | ~85 | ≥ 92 |
| Lighthouse Desktop | ~82 | ≥ 95 (requiere paid tier) |
| CLS | ~0.05 | < 0.02 |
| LCP (free tier) | 2.2s | < 1.5s |
| LCP (paid tier) | ~0.8s | < 0.8s |
| TTFB (free tier) | 1520ms | N/A (cold start) |
| TTFB (paid tier) | < 200ms | < 150ms |
| Tests | 83 | ≥ 120 |
| Cobertura | ~65% | ≥ 80% |
| Suscriptores newsletter | 0 | — |

---

## 🗓️ Historial de versiones

| Versión | Fecha | Highlights |
|---------|-------|-----------|
| v2.4.0 | 2026-03-22 | Sentry, CSP Report-Only, RSS Feed (RSS+Atom), blog cache signals, newsletter con double opt-in, FTS con SearchVector/PostgreSQL |
| v2.3.1 | 2026-03-22 | Cache signals landing, CI GitHub Actions, sitemap categorías blog, timeline animado, hero gradiente, portfolio mejorado |
| v2.3.0 | 2026-03-22 | Perf: font-display optional, reCAPTCHA async, AOS CSS defer, preconnect, carrusel 3D |
| v2.2.5 | 2026-03-21 | Seguridad: honeypot, ratelimit, DRF auth. SEO: Twitter Cards, rel=prev/next. CDN → local vendors. 83 tests |
| v2.2.0 | 2026-03-20 | Sistema mantenimiento genérico (Tabulator + MetadataMixin), delete endpoint |
| v2.1.0 | 2026-03-15 | Documentum wiki, seed SQL, setup_db command |
| v2.0.0 | 2026-03-01 | django-components-ui v1.0.0, portal privado Bootstrap 5, Glassmorphism |
