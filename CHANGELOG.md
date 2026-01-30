# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.2.5] - 2026-01-30

### 🎯 Dynamic Metrics & Admin Stability

This release introduces a dynamic metrics system for the landing page and fixes critical admin interface issues that were causing 500 errors in production.

#### Added
- ✨ **Dynamic Metrics System**: New `Metric` model for managing impact metrics from Django Admin.
    - Fields: `value`, `prefix`, `suffix`, `title`, `description`, `is_visible`, `order`
    - Custom admin interface with inline value preview and drag-to-reorder functionality
    - Automatic percentage calculation for progress ring animations
    - Template refactored to use `{% for metric in metrics %}` loop
- 🎨 **Accessibility Improvements**: Enhanced color contrast in Education Grid cards.
    - Background: Lightened to `#1e1e1e` for better visibility
    - Dates: Updated to luminous pink `#FF4081` (WCAG AA compliant)
    - Text: Brightened to `#e0e0e0` and `#d1d1d1` for AAA compliance

#### Fixed
- 🐛 **SkillAdmin**: Added missing `list_display_links = ('name',)` to prevent Django validation error when using `list_editable`
- 🐛 **ProjectAdmin**: Fixed `get_description_preview()` method to safely handle new objects (before first save) and properly render HTML with `mark_safe()`
- 🐛 **Experience Model**: Removed redundant `null=True` from `resumen` CKEditor5 field (conflicted with `default=""`)

#### Database
- 📊 **Migrations**: 
    - `0013_metric_*`: Created Metric model and related fields
    - `0014_alter_experience_resumen`: Fixed CKEditor5 field configuration

#### Verification
- ✅ **System Check**: `manage.py check` passed with no issues
- ✅ **Admin Interface**: All models now editable without 500 errors

---

## [2.2.4] - 2026-01-30

### 🚀 Performance Boost & Modernization (No-jQuery)

Major performance milestone focusing on loading speed and modernization of the frontend stack by removing legacy dependencies.

#### Performance
- ⚡ **Removed jQuery**: Completely removed `jquery-2.1.3.min.js` and all dependent plugins (OwlCarousel, Masonry, MagnificPopup) from the Landing Page.
- 📉 **Asset Reduction**: Saved **~150KB** of blocking JS/CSS scripts.
- ⚡ **HTML Minification**: Implemented `django-htmlmin` middleware to compress HTML output in production (DEBUG=False).
- 🚀 **Critical CSS**: Optimized `no-js` class handling with an inline script in `<head>` to prevent Flash of Unstyled Content (FOUC).

#### Refactored (Vanilla JS)
- 🏗️ **`main.js`**: Rewritten entirely in ES6+ Vanilla JavaScript.
    - **Navigation**: Lightweight class toggling.
    - **ScrollSpy**: Implemented using `IntersectionObserver` API (more performant than scroll listeners).
    - **Smooth Scroll**: Replaced custom logic with native `scrollIntoView`.
    - **Contact Form**: Replaced `jquery-validate` + AJAX with modern `fetch()` API.

#### Changed
- 🎨 **Typography**: Replaced JS-based `FitText` plugin with CSS `clamp()` for responsive headlines (Zero-JS approach).
- 🏗️ **Stack Definition**: Explicit separation of Public Stack (Vanilla JS + Kards CSS) vs Private Stack (Bootstrap 5).

#### Verification
- ✅ **System Check**: `manage.py check` passed.
- ✅ **Static Analysis**: Confirmed zero references to `$` or `jQuery` in public assets.

---

## [2.2.3] - 2026-01-25

### 🧹 Code Integrity & Performance Optimization

This release focuses on "Clean Code" principles, separating logic from presentation, and restoring critical SEO components after a major cleanup.

#### Refactoring & Automation (New)
- 🏗️ **Template Architecture**: Major refactor moving all templates to a centralized `app/templates` structure with clear separation between `landing` (public) and `private` (dashboard) areas.
- ⚙️ **Automated Verification**: Implemented a robust `verify_urls` management command and a Git pre-commit hook to prevent regression by verifying all critical URLs before every commit.
- 🚀 **LCP Optimization**: Fixed critical CSS image path causing 404s and delays. Added explicit preload for Hero background image to improve Largest Contentful Paint.
- 🗑️ **Cleanup**: Removed deprecated template directories and effectively centralized the frontend architecture.

#### Added
- 🧼 **Separation of Concerns**: Moved all inline CSS and `<style>` blocks from HTML templates (`base.html`, `resume.html`, `post.html`) to external `components.css`.
- 🛡️ **SEO Shield**: Restored and validated all meta-tags, Open Graph (LinkedIn/Twitter) integration, and JSON-LD structured data for better search engine ranking.
- 🎨 **Visual Rhythm**: Applied a soft gray background (`#f7f7f7`) to the "Mi Historia" section to create a cleaner visual transition between blocks.
- 🤖 **CI/CD Local**: Added `.git/hooks/pre-commit` for local quality assurance.

#### Changed
- 📐 **Grid Robustness**: Updated `.education-grid` and `.blog-grid` to ensure a consistent 3-column layout on desktop, improving responsiveness on 1024px screens.
- 📏 **Enhanced Spacing**: Increased vertical margin above the "Explorar el Blog Completo" button to **15rem** for better visual breathing room.
- 🔄 **Cache Busting**: Incremented static file versioning (v1.6) to ensure all users receive the latest visual updates immediately.
- 📂 **Project Structure**: Centralized templates in `app/templates/` (replacing `app/landing/templates`).

#### Fixed
- 🐛 **Dynamic Date Rendering**: Fixed a critical template logic error where raw Django tags were visible in the Education cards. Now correctly displays "Year - Actualidad".
- 🧩 **Template Syntax**: Repaired broken curly braces and malformed block tags in `base.html` that were causing performance lag.
- 🔗 **URL NameSpace Conflict**: Resolved Django warning `urls.W005` by removing redundant inclusion of `landing.urls` in the core configuration.
- 🔧 **Login View**: Corrected `LoginView` template path to point to the new location.
- 🐛 **Gym Namespace**: Fixed URL namespace issue in gym product list template.

---

## [2.2.2] - 2026-01-23

### 📰 Safari Compatibility & UI Polishing

This release focuses on cross-browser compatibility (especially for Safari/iOS) and UI refinements across the landing and blog sections.

#### Fixed
- 📱 **Safari Mobile Compatibility**: Resolved invisible background issue in the Intro section on iOS. Added Webkit-specific flexbox prefixes to ensure Education cards maintain their layout in Safari.
- 🌓 **Blog Dark Mode**: Implemented a higher-contrast dark theme for the blog (list and detail) specifically optimized for Safari Mac, ensuring readability when system dark mode is active.
- 🐛 **Template Syntax**: Fixed a critical syntax error in `base.html` that was affecting CSS parsing.

#### Changed
- 📋 **Blog Section Limit**: Restricted the number of featured blog posts on the landing page to 3 for a cleaner, balanced 3-column layout.
- 🖼️ **Hero Optimization**: Set Intro background to `cover` and centered position for a better visual experience on mobile devices.

---

## [2.2.0] - 2026-01-23

### ✨ UI/UX Redesign & Layout Optimization

This release introduces a major aesthetic overhaul of key landing page sections and fixes several long-standing layout and template rendering issues.

#### Added
- 🎨 **New Education Design**: Premium dark-themed, card-based layout for "Educación y Certificaciones" with modern hover effects and radial gradients.
- 🖼️ **Enhanced Portfolio Cards**: Redesigned project cards with explicit "Ver Proyecto" buttons, high-contrast badges, and smooth image zoom transitions.
- 📐 **New Centering System**: Created `app/landing/static/landing/css/centering_fixes.css` to unify row widths and centering across all sections.

#### Changed
- 📏 **Blog List Optimization**: Increased content area width to 1300px (75% column) for better readability on large screens.
- 📨 **Contact Form Overhaul**: Standardized form width to 1200px, aligning perfectly with section headers.
- 📱 **Mobile Responsiveness**: Re-optimized card stacking and padding for small devices across redesigned sections.

#### Fixed
- 🐛 **Template Tag Brokenness**: Joined split Django template tags (`{{ ... }}`) in `resume.html`, `portfolio.html`, and `base.html` that were causing hardcoded-like text rendering in the UI.
- 📐 **Education Grid Alignment**: Fixed inconsistent card heights and widths in the formation section using flexbox.
- 🔲 **Layout Mismatches**: Resolved 100px width difference between section intros and their content blocks.

#### Technical
- 🏗️ Modernized `components.css` with cleaner, class-based styles instead of inline template styling.
- 🧹 Removed redundant and conflicting layout constraints.

---

## [2.1.0] - 2026-01-18

### 🎯 Project Cleanup & Code Quality

This release focuses on comprehensive code cleanup, removing unused templates, CSS classes, and improving overall codebase maintainability. No breaking changes. 100% backwards compatible.

#### Added
- ✨ Comprehensive documentation structure (`docs/changelog/`)
- 📊 Code audit reports and metrics
- 🔍 Automated cleanup analysis tools
- 📋 Checklist for future audits
- 🏗️ Professional documentation guidelines

#### Removed
- ❌ **HTML Templates** (2 files):
  - `app/gym/templates/product_table_htmx.html` - Unused HTMX template
  - `app/gym/templates/product_table_partial.html` - Unused partial template
  
- ❌ **CSS Classes** (105 unused selectors):
  - **Grid System Legacy** (23 classes): `.col-*`, `.mob-*`, `.tab-*` 
    - Replaced by Bootstrap 5 native grid system
  - **Typography** (26 classes): `.h01-.h06`, `.percent5-.percent100`
    - No references in current templates
  - **Components** (56 classes): `.folio-*`, `.services-*`, `.pagination-*`, etc.
    - Deprecated from previous template version

- 📝 **CSS Optimization**:
  - `app/landing/static/landing/css/base.css`: -23 lines (-2.6%)
  - `app/landing/static/landing/css/main.css`: -82 lines (-3.7%)
  - **Total CSS reduction: -105 lines (-3.2%)**

#### Changed
- 🔧 **Python Views**:
  - `app/landing/views.py`: `profile()` function now redirects to `private_area`
    - Was attempting to render non-existent `landing/profile.html`
    - Now uses proper redirect pattern

#### Fixed
- 🐛 Broken template reference in `landing/views.py:32`
- 🔗 Fixed orphaned template references
- ✅ Verified all Django URLs resolve correctly

#### Security
- ✅ No security regressions
- ✅ All imports validated
- ✅ No new vulnerabilities introduced

#### Performance
- ⚡ CSS file size reduced by 3.2% (~105 lines)
- ⚡ Reduced browser parsing overhead
- ⚡ Cleaner codebase = faster development

#### Testing
- ✅ `python manage.py check` - **PASS**
- ✅ All templates render correctly
- ✅ Admin interface fully functional
- ✅ No console errors in browser
- ✅ Responsive design verified
- ✅ All URLs working as expected
- ✅ Forms (contact, login) functional
- ✅ Static files serving correctly

#### Documentation
- 📖 [INDICE_LIMPIEZA.md](changelog/INDICE_LIMPIEZA.md) - Index of cleanup documentation
- 📖 [LIMPIEZA_HTML.md](changelog/LIMPIEZA_HTML.md) - HTML template cleanup details
- 📖 [LIMPIEZA_CSS_JS.md](changelog/LIMPIEZA_CSS_JS.md) - CSS classes analysis
- 📖 [LIMPIEZA_RESUMEN.txt](changelog/LIMPIEZA_RESUMEN.txt) - Executive summary
- 📖 [INFORME_TECNICO_LIMPIEZA.md](changelog/INFORME_TECNICO_LIMPIEZA.md) - Technical report
- 📖 [CHECKLIST_AUDITORIA.md](changelog/CHECKLIST_AUDITORIA.md) - Audit checklist

#### Migration Guide
No migration needed. This release is **100% backwards compatible**.

Simply pull the latest changes and verify locally:
```bash
git pull
python manage.py check
python manage.py runserver
```

#### Known Issues
- None identified

#### Notes
- Code cleanup focused on proven non-usage
- All removed code had zero references in codebase
- Conservative approach: high-confidence removals only
- Recommendation: Next review in 30 days

---

## [2.0.0] - 2026-01-18

### 🚀 Architectural Review & Code Improvements

Major architectural review implementing modern Django best practices.

#### Added
- ✨ Modularized Django settings (`settings/base.py`, `dev.py`, `prod.py`, `test.py`)
- 📝 Comprehensive logging configuration with rotating file handlers
- 🔍 Type hints across all views (Python 3.10+ compatible)
- ✅ Model validation with `clean()` methods
- 🎨 Enhanced Django admin interface with custom displays
- 🏷️ URL namespaces (gym, blog, prompts)
- 📊 Optimized context processors with caching
- 🔒 Security improvements (CSRF, HSTS, SSL redirect in production)

#### Fixed
- 🐛 Missing imports in `blog/models.py` (strip_tags, Truncator)
- 🐛 `__str__()` methods added to 8 models
- 🐛 Logging infrastructure (print → logger)
- 🐛 Database query optimization (prefetch_related, caching)
- 🐛 Form validation improvements

#### Performance
- ⚡ Context processors now cached (1-hour TTL)
- ⚡ Database queries optimized with prefetch_related
- ⚡ Better logging configuration for production

---

## [1.0.0] - 2025-12-21

### 🎉 Initial Release

Portfolio Django application with:
- Landing page with portfolio showcase
- Blog functionality with categories
- Gym/Products management
- Private user area with prompts
- Admin interface customization
- Bootstrap 5 responsive design

---

## Future Improvements (Roadmap)

### v2.2.0 (Planned)
- [ ] Migrate jQuery to vanilla JavaScript (remove jquery-2.1.3.min.js)
- [ ] Self-host fonts for better performance
- [ ] Minify CSS for production
- [ ] Implement critical CSS
- [ ] Add pytest test suite

### v2.3.0 (Planned)
- [ ] Migrate to Tailwind CSS (optional)
- [ ] Add dark mode support
- [ ] Implement service worker (PWA)
- [ ] Add Google Analytics integration

### v3.0.0 (Planned)
- [ ] Django upgrade to 7.0+
- [ ] Python 3.13+ support
- [ ] Full TypeScript migration (if frontend needed)
- [ ] API first architecture (DRF)

---

## How to Contribute

### Reporting Issues
1. Describe what went wrong
2. Describe what you expected
3. Include steps to reproduce
4. Check existing issues first

### Pull Requests
1. Create feature branch from `main`
2. Make your changes
3. Add/update documentation
4. Test locally: `python manage.py check`
5. Submit PR with clear description

### Code Quality Standards
- ✅ Type hints for all functions
- ✅ Docstrings for complex logic
- ✅ `python manage.py check` must pass
- ✅ No console errors
- ✅ Backwards compatible (or versioned)

---

## Release Notes

### Support
- **Python**: 3.12+
- **Django**: 6.0+
- **Database**: PostgreSQL (Supabase) / SQLite (dev)
- **Hosting**: Render.com

### Security
For security issues, email to: [contact info] instead of creating public issues.

---

## Maintenance Status

| Version | Status | Until |
|---------|--------|-------|
| 2.1.x | Active | 2026-06-18 |
| 2.0.x | Maintenance | 2026-04-18 |
| 1.0.x | Deprecated | 2026-02-18 |

---

## Archive

All historical releases and their documentation are available in `docs/changelog/`

