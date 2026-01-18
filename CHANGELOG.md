# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

