# 📚 Índice Central — HernandezPalo Portfolio

**Punto de entrada único para toda la documentación del proyecto.** Léelo primero, luego navega a las secciones que necesites.

---

## 🚀 Empezar rápido

1. **Nuevo en el proyecto** → Lee `1-ARQUITECTURA.md` (visión general)
2. **Necesito desplegar** → Ve a `4-DESPLIEGUE.md`
3. **Tengo un error** → Consulta `6-TROUBLESHOOTING.md`
4. **Quiero añadir componentes UI** → Estudia `3-COMPONENTES.md`
5. **Datos y analytics** → Revisa `7-ANALYTICS.md`

---

## 📖 Secciones principales

| Documento | Propósito | Para quién |
|---|---|---|
| **`1-ARQUITECTURA.md`** | Visión del sistema, stack técnico, estructura de apps, patrones de código | Arquitectos, leads, nuevos desarrolladores |
| **`2-APPS.md`** | Guía por app: responsabilidades, modelos, vistas, ejemplos de código | Desarrolladores que trabajan en apps específicas |
| **`3-COMPONENTES.md`** | Catálogo completo de `django-components-ui` + instalación + uso | Desarrolladores de frontend, designers |
| **`4-DESPLIEGUE.md`** | CI/CD en Render, variables de entorno, setup post-deploy, backup | DevOps, maintainers |
| **`5-TESTING.md`** | Testing, setup_db, seeding, verificación pre-commit | QA, desarrolladores |
| **`6-TROUBLESHOOTING.md`** | Errores comunes, debugging, soluciones rápidas | Todos (referencia constante) |
| **`7-ANALYTICS.md`** | Dashboard analytics privacy-first, tracking sin cookies, trending de posts | Product managers, data analysts |

---

## 🔗 Referencias rápidas

### Para Claude Code / IA
- **`../CLAUDE.md`** ← Reglas operativas (la autoridad máxima)
- Memoria en `/Users/hernandezpalo/.claude/projects/...` (contexto persistente)

### Stack técnico
```
Backend:  Django 5.1 + DRF (privado) + PostgreSQL (Supabase)
Frontend: Tailwind + Bootstrap 5 (dual-stack)
Deploy:   Render (main branch auto-deploy)
DB Local: SQLite
Analytics: Privacy-first (sin cookies), IP-API.com
```

### Estructura de carpetas
```
app/
├── landing/     → Hub principal + Portal privado (/private/)
├── blog/        → CMS de posts + SEO
├── documentum/  → Wiki técnica (/wiki/)
├── gym/         → Inventario + Mantenimiento tabular
├── prompts/     → Biblioteca IA (No-DB, GitHub API)
├── analytics/   → Analytics + Dashboards (/private/analytics/)
└── config/      → Settings, URLs, logging
```

---

## ⚡ Reglas de oro

1. **Dual-Stack UI**: Tailwind + components_ui en público (`/`), Bootstrap 5 en privado (`/private/`)
2. **Logging**: Siempre `logging.getLogger()`, **nunca** `print()`
3. **SEO**: Cada vista pública necesita meta tags + sitemap
4. **Backup**: Los datos de `gym` y `landing` se persisten en `db_backup.json` (crítico en Render)
5. **Componentes**: Usa siempre tags de `components_ui` en lugar de HTML manual
6. **Analytics**: Middleware captura automáticamente, ejecutar `manage.py update_analytics` diariamente

---

## 🛠️ Tareas comunes

### ¿Cómo añado una nueva vista?
→ Sección "Patrón de Vistas" en `1-ARQUITECTURA.md`

### ¿Cómo creo un CRUD tabular?
→ Sección "Sistema de Mantenimiento" en `1-ARQUITECTURA.md` (receta canónica)

### ¿Cómo hago un backup / restauro datos?
→ Sección "Resiliencia y Backup" en `4-DESPLIEGUE.md`

### ¿Por qué falla collectstatic?
→ Sección "sourceMappingURL" en `6-TROUBLESHOOTING.md`

### ¿Cómo añado un nuevo endpoint de API?
→ Sección "API (DRF)" en `1-ARQUITECTURA.md`

### ¿Cómo veo los datos de analytics?
→ Dashboards en `/private/analytics/` después de `manage.py update_analytics`

---

## 📊 Analytics Setup

1. Migraciones ya hechas: `migrate analytics`
2. Middleware activo: captura automática en cada request
3. Ejecutar: `python manage.py update_analytics`
4. Visitar: `/private/analytics/` (login requerido)
5. Programar diariamente: Celery o cron

Ver `7-ANALYTICS.md` para detalles completos.

---

## 📝 Última actualización

- **Consolidado**: 2026-09-25
- **Versión del proyecto**: Django 5.1+, Python 3.11+
- **Apps**: landing, blog, documentum, gym, prompts, analytics, config
- **Maintainer**: Hernández Palo (@hernandezpalo)

> **Nota**: Este índice es dinámico. Si encuentras información desactualizada o referencias rotas, actualiza este archivo inmediatamente.
