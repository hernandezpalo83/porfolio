# ROADMAP — HernandezPalo Portfolio

> Registro de ideas, mejoras y funcionalidades futuras. Priorizado por impacto y viabilidad.
> Estado: `[ ]` pendiente · `[~]` en progreso · `[x]` completado

---

## 🎯 Prioridad Alta — Quick Wins

### FEAT-001 · Sección "Recetas" en el portal privado
**Descripción:** Nuevo apartado en el menú privado con plantillas de código listas para funcionar.
Cada receta sería una página HTML copiable con instrucciones de uso.

Recetas planificadas:
- `recipe-login` — Login funcional con Django `AuthenticationForm`, CSRF, mensajes de error, redirección
- `recipe-crud` — CRUD completo: listado (Tabulator), formulario de alta, confirmación de borrado
- `recipe-app-starter` — Plantilla base: navbar + sidebar + layout inicial para empezar una app

**Valor:** Acelera el desarrollo de nuevos proyectos Django. Referencia interna de patrones canónicos.
**Complejidad:** Media · Estimación: 1 sesión

---

### FEAT-002 · Nuevos componentes en `django-components-ui`
**Descripción:** Ampliar la librería con componentes de alta utilidad detectados en el uso real.

Componentes propuestos:
- `comp_login_form` — Formulario de login completo con CSRF, errores, remember me
- `comp_empty_state` — Estado vacío con icono, título, descripción y botón de acción
- `comp_stat_grid` — Grid de KPI cards responsive (wrap de `comp_data_card`)
- `comp_search_bar` — Barra de búsqueda standalone con filtros y debounce
- `comp_confirm_action` — Confirmación de acción destructiva inline (sin modal)
- `comp_copy_button` — Botón "copiar al portapapeles" con feedback visual

**Valor:** Reducir tiempo de desarrollo de nuevas vistas en todos los proyectos que usen la librería.
**Complejidad:** Media · Estimación: 2-3 sesiones

---

### FEAT-003 · Cache invalidation signals
**Descripción:** Cuando el admin modifica datos de `landing` (Info, Skills, Projects, Metrics, Companies),
invalidar automáticamente la caché `landing_home_data` sin intervención manual.

```python
# landing/signals.py
from django.db.models.signals import post_save
from django.core.cache import cache

def invalidate_home_cache(sender, **kwargs):
    cache.delete('landing_home_data')

post_save.connect(invalidate_home_cache, sender=Info)
# ... mismo para Skill, Project, Metric, CompanyCollaboration
```

**Valor:** El admin ve los cambios reflejados inmediatamente en producción sin necesidad de reiniciar.
**Complejidad:** Baja · Estimación: 30 min

---

### FEAT-004 · Upgrade Render a paid tier
**Descripción:** El TTFB actual en producción es ~1500ms debido al cold start de Render free tier.
Con el plan Starter ($7/mes) el servidor está siempre caliente → TTFB < 200ms.

**Impacto estimado en Lighthouse desktop:** +15-20 puntos (LCP 2.2s → ~0.8s)
**Valor:** Mejora drástica de Core Web Vitals y UX real. Mayor score de Google para indexación.
**Complejidad:** Ninguna (es un cambio de plan) · Coste: $7/mes

---

## 🛠️ Mejoras Técnicas

### TECH-001 · Sitemap de categorías del blog
**Descripción:** Actualmente el sitemap incluye posts individuales pero no las URLs de categorías.
Añadir `CategorySitemap` con `lastmod` dinámico basado en el post más reciente de cada categoría.

**Valor:** Mejora la indexación de `/blog/<category-slug>/` por los crawlers.
**Complejidad:** Baja · Estimación: 20 min

---

### TECH-002 · Optimización de imágenes del perfil y CDN
**Descripción:** La imagen de perfil se carga desde GitHub CDN sin `srcset`.
Lighthouse detecta ~27KB de ahorro. Añadir:
- `srcset` para servir tamaños distintos según viewport
- Versión 2x para pantallas retina
- Considerar Cloudinary o similar si el CDN de GitHub da latencia

**Valor:** Menor peso de página, mejor LCP y score de Lighthouse.
**Complejidad:** Baja-Media · Estimación: 1h

---

### TECH-003 · CSP (Content Security Policy)
**Descripción:** Añadir cabeceras CSP en Render o mediante middleware Django.
Política inicial permisiva → ir reforzando progresivamente.

**Riesgo:** Alto si se configura mal (puede romper reCAPTCHA, AOS, etc.).
**Recomendación:** Usar `Report-Only` primero para auditar sin bloquear.
**Complejidad:** Alta · Estimación: 2-3 sesiones con testing

---

### TECH-004 · Tests de integración E2E (Playwright)
**Descripción:** Complementar los tests unitarios/integración actuales con tests E2E que:
- Naveguen la landing page
- Rellenen y envíen el formulario de contacto (con mock de reCAPTCHA)
- Verifiquen el blog listado y detalle de post

**Valor:** Detectar regresiones visuales y de flujo antes de cada deploy.
**Complejidad:** Media · Estimación: 2 sesiones

---

### TECH-005 · Tailwind CSS build local (sin CDN)
**Descripción:** Sustituir el CDN de Tailwind en el área pública por un build local con PurgeCSS.
El CDN actual muestra un warning en consola y carga ~350KB de CSS sin usar.

**Proceso:**
```bash
npm init -y
npm install -D tailwindcss
npx tailwindcss init
# Configurar purge paths → build → copiar a static/
```

**Valor:** Eliminar warning de Tailwind CDN, reducir peso CSS en ~340KB.
**Complejidad:** Alta (requiere CI/CD build step) · Estimación: 1 sesión + CI config

---

### TECH-006 · Monitorización con Sentry
**Descripción:** Integrar Sentry para captura de errores en producción con contexto completo.

```python
# requirements.txt
sentry-sdk[django]

# settings/production.py
import sentry_sdk
sentry_sdk.init(dsn=env('SENTRY_DSN'), traces_sample_rate=0.1)
```

**Valor:** Alertas en tiempo real cuando algo falla en producción. Fundamental para TPM.
**Complejidad:** Baja · Estimación: 30 min · Coste: Free tier de Sentry

---

### TECH-007 · GitHub Actions para CI
**Descripción:** Añadir workflow de GitHub Actions que ejecute los 83 tests en cada PR antes de mergear.

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python manage.py test
```

**Valor:** Nunca mergear código roto. Barrera de calidad automatizada.
**Complejidad:** Baja · Estimación: 30 min

---

## ✨ Funcionalidades Nuevas

### NEW-001 · Formulario de contacto con feedback en tiempo real
**Descripción:** Mejorar el formulario de contacto actual con:
- Validación en tiempo real con Vanilla JS (sin esperar al submit)
- Spinner durante el envío
- Mensaje de éxito/error inline sin recargar la página (fetch API)
- Contador de caracteres en el campo "mensaje"

**Valor:** UX mucho más fluida. Reduce abandono del formulario.
**Complejidad:** Media · Estimación: 1-2 sesiones

---

### NEW-002 · Modo oscuro
**Descripción:** Dark mode toggle persistido en `localStorage`.
Usar CSS custom properties (`--color-bg`, `--color-text`, etc.) para facilitar el cambio.

**Reto:** El área pública usa un tema heredado (Kards) que no está construido con custom properties.
Sería necesario refactorizar el CSS progresivamente o añadir una capa de override.

**Valor:** Mejora la experiencia para el ~82% de usuarios que prefieren dark mode.
**Complejidad:** Alta · Estimación: 3-4 sesiones

---

### NEW-003 · Newsletter / Suscripción al blog
**Descripción:** Formulario simple de suscripción (email + nombre) con:
- Modelo `Subscriber` en `blog`
- Email de confirmación (double opt-in)
- Integración con Mailchimp API o envío directo con SendGrid
- Vista de admin para gestionar suscriptores

**Valor:** Construir audiencia recurrente. Demostrar gestión de producto con canal propio.
**Complejidad:** Media · Estimación: 2-3 sesiones

---

### NEW-004 · Búsqueda global con Algolia o Postgres Full-Text Search
**Descripción:** Barra de búsqueda en el navbar que devuelva resultados de:
- Posts del blog
- Documentos de la wiki
- Secciones de la landing

Opciones:
- **Django + Postgres FTS**: Sin coste adicional, `SearchVector` + `SearchQuery`
- **Algolia**: Mejor UX, autocomplete instantáneo, plan free generoso

**Valor:** Navegación mucho más rápida para visitantes técnicos.
**Complejidad:** Media-Alta · Estimación: 2-3 sesiones

---

### NEW-005 · Estadísticas de visitas (Privacy-first)
**Descripción:** Integrar una alternativa a Google Analytics que respete la privacidad y no requiera cookie banner:
- **Umami** (self-hosted en Railway/Fly.io) — Open source
- **Plausible** ($9/mes) — Dashboard elegante
- **Fathom** ($14/mes) — Más minimalista

Métricas a trackear: páginas vistas, posts más leídos, países de origen, fuentes de tráfico.

**Valor:** Datos reales de audiencia sin comprometer la privacidad ni añadir cookie banner.
**Complejidad:** Baja · Estimación: 1h

---

### NEW-006 · API pública del blog (RSS/JSON Feed)
**Descripción:** Exponer los posts del blog mediante:
- **RSS feed** (`django.contrib.syndication`) — Estándar, compatible con lectores RSS
- **JSON Feed** — Alternativa moderna al RSS

**Valor:** Distribución automática del contenido. Permite integración con herramientas externas.
**Complejidad:** Baja · Estimación: 1h

---

### NEW-007 · Internacionalización (i18n) — Versión en inglés
**Descripción:** Añadir versión en inglés de la landing page y el blog.
Usar `django.utils.translation` + `LocaleMiddleware`.

**Reto:** Requiere traducir todos los textos hardcodeados en templates y modelos.
**Valor:** Ampliar audiencia al mercado anglosajón. Muy relevante para posicionamiento internacional.
**Complejidad:** Alta · Estimación: 5-7 sesiones

---

## 🎨 Mejoras Visuales

### VIS-001 · Sección de Testimonios / Recomendaciones
**Descripción:** Nueva sección en la landing con citas de personas que han trabajado conmigo.
Datos desde LinkedIn o introducidos manualmente en el admin.

**Estructura:**
- Foto + nombre + cargo + empresa + cita
- Carousel o grid 3 columnas
- Enlace al perfil de LinkedIn

**Valor:** Social proof. Humaniza el portfolio y aumenta la confianza de los visitantes.
**Complejidad:** Baja · Estimación: 1 sesión

---

### VIS-002 · Animación del timeline de experiencia
**Descripción:** El timeline de experiencia actual es estático.
Añadir una animación de "dibujo de línea" que se completa mientras el usuario hace scroll.

**Técnica:** CSS `stroke-dasharray` / `stroke-dashoffset` + IntersectionObserver (igual que las métricas).

**Valor:** Efecto visual memorable y técnicamente impresionante.
**Complejidad:** Media · Estimación: 1 sesión

---

### VIS-003 · Gradiente animado en la sección hero
**Descripción:** El fondo de la sección intro es una imagen estática.
Añadir un gradiente animado CSS sutil como overlay (`@keyframes` con `background-position`).

**Valor:** Da más vida al hero sin imágenes adicionales. Impacto visual en el primer scroll.
**Complejidad:** Baja · Estimación: 30 min

---

### VIS-004 · Proyecto Showcase mejorado
**Descripción:** Las tarjetas de proyectos actuales son informativas pero no destacan.
Mejorar con:
- Imagen/mockup del proyecto (screenshot o maqueta)
- Tag de tecnologías usadas (Django, React, PostgreSQL...)
- Indicador de estado (En producción / En desarrollo / Archivado)
- Enlace a demo o repositorio GitHub

**Valor:** Los proyectos son el core del portfolio técnico. Mejor presentación = más impacto.
**Complejidad:** Media · Estimación: 1-2 sesiones

---

## 📊 Métricas y Objetivos

| Métrica | Actual | Objetivo |
|---|---|---|
| Lighthouse Mobile (Performance) | ~85 | ≥ 92 |
| Lighthouse Desktop (Performance) | 66 → ~82* | ≥ 90 |
| CLS | 0.394 | < 0.05 |
| LCP | 2.2s | < 1.5s |
| TTFB | 1520ms | < 200ms (requiere paid tier) |
| Tests | 83 | > 120 |
| Cobertura | ~65% | ≥ 80% |

*Estimado tras los fixes de esta sesión (font-display, preconnect, reCAPTCHA async, AOS CSS)

---

## 🗓️ Historial de versiones

| Versión | Fecha | Highlights |
|---|---|---|
| v2.3.0 | 2026-03-22 | Performance: font-display optional, reCAPTCHA async, preconnect, AOS CSS defer, carrusel 3D |
| v2.2.5 | 2026-03-21 | Public area hardening: CDN → local vendors, Twitter Cards, CLS fixes, 83 tests |
| v2.2.0 | 2026-03-20 | Generic maintenance system (Tabulator), metadata API, delete endpoint |
| v2.1.0 | 2026-03-15 | Documentum wiki, seed SQL, setup_db command |
| v2.0.0 | 2026-03-01 | django-components-ui v1.0.0, private portal Bootstrap 5, Glassmorphism |
