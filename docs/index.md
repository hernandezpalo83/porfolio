# Documentación — Proyecto Porfolio 📚

Bienvenido a la documentación del proyecto. Esta carpeta contiene guías operativas, de despliegue y de mantenimiento en Markdown y está organizada por categorías para ser indexada en `/wiki/`.

## Categorías principales

- 📦 **Operations** — /wiki/operations/  
  - Despliegue en Render — `Despliegue en Render` (usa `setup_db` y seed SQL)
  - Seeding y generación de SQL
- 🧑‍💻 **Developer** — /wiki/developer/  
  - Testing y contribución (pre‑commit, verify_urls)
- 📚 **Documentum** — /wiki/documentum/  
  - Introducción y flujo de trabajo para documentación
- 🛠️ **Troubleshooting** — /wiki/troubleshooting/  
  - Errores frecuentes y soluciones rápidas
- 🏗️ **Architecture** — /wiki/architecture/  
  - Resumen de la arquitectura del proyecto

---

Para importar estas páginas en la app `documentum` (y que aparezcan en `/wiki/`): guarda los MD en `/docs/<category>/` (ya están organizados) y ejecuta:

```bash
python manage.py seed_documentum
# o
python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render
```

> Tip: Mantén una breve línea de resumen justo después del `# Título` — el generador la utiliza como meta‑descripción para la página.