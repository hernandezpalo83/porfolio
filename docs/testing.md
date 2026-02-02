# Testing

Guía rápida para ejecutar test y comprobaciones locales.

## Ejecutar test
- Ejecuta todos los tests:
```bash
python manage.py test
```
- Ejecutar tests de un app concreto (p.ej. documentum):
```bash
python manage.py test app.documentum
```

## Pre-commit checks
- El proyecto tiene hooks que verifican URLs con `python manage.py verify_urls`.
- Si un commit falla, revisa los logs y arregla las rutas o dependencias antes de intentar de nuevo.

## Tests recomendados
- Test de integración para `setup_db` (seed + normalize + render).
- Tests de vista para `/wiki/` para comprobar status 200 y templates utilizados.