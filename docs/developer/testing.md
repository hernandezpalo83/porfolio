# Testing — Guía rápida ✅

**Resumen:** Cómo ejecutar los tests y buenas prácticas para añadir tests en PRs.

```bash
python manage.py test
python manage.py test app.documentum
```

- Ejecuta `python manage.py verify_urls` como parte de pre-commit.
- Añade tests de integración para `setup_db` cuando introduzcas changes en seed/normalization.
