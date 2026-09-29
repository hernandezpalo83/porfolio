# CLAUDE.md — HernandezPalo Portfolio (Optimized for Claude Code)

## 1. Project Profile & TPM Standard
- **Purpose**: Professional portfolio & Technical Product Management CMS (hernandezpalo.es).
- **Core Strategy**: High-resilience architecture, advanced SEO, full-stack execution, zero anti-patterns.
- **Rule**: Every technical decision is intentional and persistent. Never introduce quick-fix slop.

---

## 2. Tech Stack & Infrastructure
- **Backend**: Django 5.1+ | Python 3.11+ (Functions with type hints `HttpRequest -> HttpResponse`; NO CBVs except `django-filters.FilterView`).
- **APIs**: DRF (Internal Tabulator maintenance endpoints ONLY via `/metadata/` + `ModelViewSet`).
- **Database**: PostgreSQL / Supabase (`dj-database-url`, SSL) in Prod | SQLite in Dev (`DATABASE_URL` check).
- **Public UI**: Vanilla JS ES6+ | Custom CSS (Kards) | Tailwind CSS (Dev CDN only, strictly no build in prod) | Heroicons v2 (`{% load components_ui %}`).
- **Private UI** (`/private/`): Bootstrap 5.3 + Glassmorphism (`.card-gemini`) | Bootstrap Icons | Tabulator JS 6.2.1.
- **Components Library**: `django-components-ui` (Private GitHub pkg; dev mode: `pip install -e /path/to/pkg`). Tags: `comp_tabla_mantenimiento`, `comp_tabla`, `comp_card`, `comp_button`, `comp_badge`, `comp_tabs`, `comp_acordeon`, `comp_breadcrumbs`.
- **Rich Text / Sanitization**: `django-ckeditor-5` + `bleach>=6.0.0` (Use `{{ content|sanitize_html }}`).
- **Static Assets**: WhiteNoise + `CompressedManifestStaticFilesStorage` (1yr cache) | `django-htmlmin` (`DEBUG=False`).
- **Async & Security**: Celery 5.3+ + Redis 5.0+ (Batch Analytics) | `django-csp>=3.7` (Nonce-based ENFORCE mode: `<script nonce="{{ csp_nonce }}">`).
- **Deployment**: Render Web Service (CI/CD from `main`) | CDN: `BRAND_ASSETS_URL` (GitHub raw).

---

## 3. Search & File Exclusions (.claudeignore Enforcement)
- **Do NOT inspect/search**: `.venv/`, `node_modules/`, `staticfiles/`, `media/`, `app/logs/`, `*.egg-info/`, `.git/`, `*.sqlite3`
- **Avoid full test suites**: Always execute targeted module tests first.

---

## 4. Dual-Stack UI Enforcement (STRICT)
- **Public Area (`/`, `/blog/`, `/wiki/`)**: Tailwind CSS + `components_ui` (`comp_*`) + Heroicons v2 + Vanilla JS. NO Bootstrap. NO jQuery.
- **Private Area (`/private/`)**: Bootstrap 5.3 (`private_portal.css`) + Bootstrap Icons + Tabulator JS. NO Tailwind.

---

## 5. Architectural Conventions & Tabulator Pattern
- **Models**: Business logic & validation inside `clean()`, never in views. Define `Meta.ordering`, `__str__`, and audit timestamps (`created_at`/`fecha_creacion`). Field languages: Spanish (`gym`/`landing`), English (`blog`).
- **Canonical Tabulator CRUD**:
  1. `serializers.py` -> `ModelSerializer(fields='__all__')`
  2. `api.py` -> `MetadataMixin + ModelViewSet` at `/<app>/api/<model>-api/`
  3. `views.py` -> Pass `cols` (Tabulator config) + `api_url`
  4. `template` -> Extend `private/layouts/base.html` + `{% comp_tabla_mantenimiento data_url=api_url columns=cols searchable=True filterable=True %}`
- **URL Namespaces**: Always use defined namespaces: `blog:`, `gym:`, `wiki:`, `landing:private_*`.
- **Logging**: NEVER use `print()`. Use `import logging; logger = logging.getLogger(__name__)`.

---

## 6. Execution Commands
```bash
# Development & Verification
PYTHONPATH=. python app/manage.py test
PYTHONPATH=. python app/manage.py test app.<app_name>
PYTHONPATH=. python app/manage.py verify_urls

# Pre-Deploy Verification (MUST run with DEBUG=False)
DEBUG=False SECRET_KEY=test PYTHONPATH=. python app/manage.py collectstatic --noinput --clear
```

---

## 7. Render Build & Backup Strategy
- **Render Build Command**:
  `pip install -r requirements.txt && python app/manage.py migrate && python app/manage.py setup_db && python app/create_admin.py && python app/manage.py collectstatic --noinput`
- **Data Persistence**: Data persists via `db_backup.json`. Warn user if schema changes risk breaking `setup_db` restore/seed logic. Disaster recovery seed: `python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render`.
- **Diagnostics**: Superuser endpoint `GET /api/debug/diagnostics/` or panel at `/private/`.

---

## 8. Anti-Patterns (STRICT PROHIBITIONS)
- ❌ **NO `print()`**: Use `logging`.
- ❌ **NO Stack Blending**: Do not mix Bootstrap and Tailwind in the same template.
- ❌ **NO Unsanitized HTML**: Never use `|safe` for user/CKEditor input; use `|sanitize_html`.
- ❌ **NO Orphan `sourceMappingURL`**: Strip `//# sourceMappingURL=*.map` from vendor JS if `.map` is missing (breaks WhiteNoise).
- ❌ **NO Missing SEO**: Public views must include `<title>`, `<meta name="description">`, OpenGraph, and Sitemap integration.
- ❌ **NO Hardcoded CDN URLs**: Always reference `BRAND_ASSETS_URL` from settings.
- ❌ **NO Uncommitted Requirements**: Always verify dependencies exist in `requirements.txt`.
- ❌ **NO Realistic API Keys in CI**: Use fake keys (`ci-fake-*`) in `ci.yml` to prevent GitGuardian PR block.
- ❌ **NO CI Failures**: Check imports with `ruff check app/ --select F401,F811,E711,E712` before merging. Always set `PYTHONPATH` in CI.
- ❌ **NO `app/static/`**: Django does not serve it (`STATICFILES_DIRS = []`) → 404. Landing statics live in `app/landing/static/landing/`.
- ❌ **NO CKEditor HTML inside `<p>`**: The content brings its own `<p>`; browsers eject them from the wrapper. Use a `<div>`.
- ❌ **NO 16px `rem` assumptions in landing**: `html { font-size: 62.5% }` → `1rem = 10px`.
- ❌ **NO `#CC0052` text on dark / `#FF0077` on light**: Fails WCAG AA. Use `#CC0052` on light, `#FF1493` on dark (`var(--accent-primary)` handles it).
- ❌ **NO icon fonts in public pages**: Use `{% load ui %}{% icon "name" %}` (SVG sprite in `landing/components/icon_sprite.html`). Font Awesome 6 is only loaded, non-blocking, in wiki pages with DB-driven category icons.
- ❌ **NO AOS / animation libraries**: Use `data-reveal` (IntersectionObserver in `main.js`); content must stay visible without JS.
- ❌ **NO `request.scheme` / `build_absolute_uri` for canonical, OG or JSON-LD**: Render's proxy makes them `http://`. Use `{{ SITE_URL }}{{ request.path }}`; escape JSON-LD strings with `|json_str`.
- ❌ **NO more than one `<h1>` per page**: Section titles are `<h2 class="section-heading">`, eyebrows `<p class="section-eyebrow">`.
- ❌ **NO generic element selectors (`header`, `nav`) with layout in `bundle.v2.css`**: They leak into article headers and breadcrumbs. Scope them with a class.
- ❌ **NO per-section paddings or fixed hero heights**: Home sections take their spacing from `--section-space` / `--section-head-gap` (`critical_css.html`), and the navbar offset from `--header-h` (updated by `main.js`). Never add `padding: 12rem 0` to a section or `height`/`translate` to the hero, or content will slide under the fixed navbar.
- ❌ **NO inline event handlers or un-nonced inline scripts in public templates**: The public CSP is enforced (`CONTENT_SECURITY_POLICY`). Inline `<script>` needs `nonce="{{ request.csp_nonce }}"` (not available inside form widgets: use a static JS file); async CSS uses `media="print" data-async-css`, never `onload=`. Private prefixes are listed in `CSP_PRIVATE_PREFIXES`.
- ❌ **NO blocking work in middleware**: No external HTTP calls or synchronous remote DB writes per request. Analytics stores no IP/user-agent (anonymous daily hash, country from `CF-IPCountry`) and writes off the request path.
- ❌ **NO personal data without a retention rule**: Retention promised in `/privacidad/` is applied by `purge_personal_data` (run by `setup_db` on every deploy). Update both if it changes.

---

## 9. Compact & Output Protocol
- **On `/compact`**: Preserve current active session decisions, pending TODOs, and modified file paths. Drop console logs and raw file dumps.
- **Output Style**: Direct, code-first answers. Omit conversational intros/outros. Modify code directly without line-by-line summaries unless requested.