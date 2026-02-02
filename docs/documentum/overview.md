# Documentum — Introducción 📚

**Resumen:** El módulo `app.documentum` gestiona la documentación pública del proyecto y se expone en `/wiki/`.

## Estructura
- Categorías: basadas en carpetas (p.ej. `operations`, `developer`).
- Documentos: archivos Markdown con un título `# Título` como primer encabezado.

## Flujo de trabajo
1. Añade o modifica MD en `/docs/<category>/`.
2. Ejecuta `python manage.py seed_documentum` para importar desde Markdown (o genera SQL y ejecútalo).
3. Ejecuta `python manage.py render_documentum_html --force` o `python manage.py setup_db --render-only --force` para generar HTML.

## Buenas prácticas
- Mantén un resumen en la segunda línea del MD para que el generador lo use como meta descripción.
- Revisa y añade pruebas si cambias estructuras de documentos.
