# Arquitectura — Resumen visual y componentes 🏗️

**Resumen:** Componentes principales y responsabilidades.

- Django monorepo con apps: `landing`, `documentum`, `blog`, `gym`, `prompts`.
- Postgres en producción (Supabase), SQLite en tests locales.
- Backups: `db_backup.json` y seeding automatizado mediante `setup_db`.

Para detalles operativos ver `docs/operations/deployment.md` y `docs/documentum/overview.md`.