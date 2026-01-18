# 📖 INSTRUCCIONES DE USO - CAMBIOS IMPLEMENTADOS

Después de la revisión arquitectónica, aquí está cómo usar el proyecto mejorado.

---

## 🚀 INICIO RÁPIDO

### Desarrollo Local (Default):
```bash
cd /Users/hernandezpalo/Documents/Javi/Desarrollo/Django/porfolio

# Instalar dependencias (si es necesario)
pip install -r requirements.txt

# Migrar BD
python manage.py migrate

# Ejecutar servidor
python manage.py runserver
# → http://127.0.0.1:8000/
```

### Testing Local:
```bash
DJANGO_ENV=development python manage.py runserver
# (settings/development.py - DEBUG=True, logging verbose)
```

---

## 🔧 USAR DIFERENTES ENTORNOS

### 1. Development (Default - Local)
```bash
# Automático si DJANGO_ENV no está set
python manage.py runserver
```

**Características**:
- DEBUG = True
- Logging en consola (verbose)
- SQLite o PostgreSQL según configuración
- Todas las herramientas de debug disponibles

### 2. Production (Render)
```bash
DJANGO_ENV=production gunicorn app.config.wsgi
```

**Agregar en Render**:
- Environment Variable: `DJANGO_ENV=production`

**Características**:
- DEBUG = False
- HTTPS obligatorio
- HSTS habilitado
- Logging a archivo (logs/django_production.log)
- Password validators activados

### 3. Testing
```bash
DJANGO_ENV=testing pytest
# o
DJANGO_ENV=testing python manage.py test
```

**Características**:
- BD en memoria (:memory:)
- Password hashing rápido (solo para tests)
- Logging silencioso

---

## 📊 USAR VALIDACIONES EN MODELOS

### En Admin (Automático):
Cuando intentas guardar datos inválidos, Django valida automáticamente:

```
❌ Skill con score = 150
   Error: "Score debe estar entre 0 y 100"

❌ Experience: end_date = 2020-01-01, start_date = 2020-12-31
   Error: "La fecha de fin no puede ser anterior a la de inicio"

❌ Product: price = $50, cost = $100
   Error: "El precio no puede ser menor al costo"
```

### En Código (Explícito):
```python
from app.landing.models import Skill
from django.core.exceptions import ValidationError

skill = Skill(name='Python', score=105)

try:
    skill.full_clean()  # Ejecuta validaciones
    skill.save()
except ValidationError as e:
    print(f"Error: {e}")
```

---

## 🎨 USAR ADMIN MEJORADO

### Cambios de UX:

#### 1. **ProjectAdmin** (Landing)
Antes: HTML en el listado (lento)
Ahora: Descripción corta de 50 caracteres
```
Listado más rápido ⚡
Preview HTML en readonly ✅
```

#### 2. **SkillAdmin** (Landing)
Antes: Solo nombre
Ahora: Editable inline + ordenado por score
```
Cambiar skills directamente sin entrar 🎯
Mejores skills primero (score descendente) 📊
```

#### 3. **ProductAdmin** (Gym)
Antes: Solo datos básicos
Ahora: Margen de ganancia calculado + editable status
```
Ver ROI directamente en el listado 💰
Cambiar status sin entrar 🎯
```

#### 4. **ProductoAdmin** (Gym)
Antes: Descripción completa (lento)
Ahora: Descripción corta + fieldsets colapsables
```
Carga rápida ⚡
Auditoría en sección collapse 🔍
```

---

## 🔗 USAR NAMESPACES DE URLS

### Antes:
```html
<a href="{% url 'lista_productos' %}">Productos</a>
<!-- ¿De qué app? Ambiguo -->
```

### Después:
```html
<a href="{% url 'gym:lista_productos' %}">Productos</a>
<!-- Claro: app gym, vista lista_productos -->

<a href="{% url 'gym:product_list' %}">Products (HTMX)</a>
<a href="{% url 'prompts:prompt_library' %}">Prompts</a>
```

### En Vistas:
```python
from django.urls import reverse

url = reverse('gym:lista_productos')
# → /gym/productos/
```

---

## 📝 TYPE HINTS - IDE SUPPORT

### Beneficios:

#### 1. Autocomplete Mejorado:
```python
def home(request: HttpRequest) -> HttpResponse:
    # IDE sabe que request tiene .method, .GET, .POST, etc.
    # IDE sabe que debes retornar HttpResponse
```

#### 2. Detectar Errores Antes de Ejecutar:
```python
# ❌ mypy/pyright detectaría esto:
def get_info() -> Info:
    return None  # Error: None no es Info

# ✅ Correcto:
from typing import Optional
def get_info() -> Optional[Info]:
    return None  # OK
```

#### 3. Auto-Documentación:
```python
def export_data_view(request: HttpRequest) -> HttpResponse:
    # Solo leyendo la firma, sé exactamente qué espera y qué retorna
```

### Agregar Más Type Hints:
```bash
# Instalar mypy para verificación estática
pip install mypy

# Verificar tipos
mypy app/
```

---

## 📚 LOGGING - ACCEDER A TRAZAS

### Desarrollo (Consola):
```bash
python manage.py runserver 2>&1 | grep -i error
# Los logs aparecen en la consola
```

### Producción (Archivo):
```bash
tail -f app/logs/django_production.log
# O en Render: Ver en logs web

# Ejemplo de log:
[ERROR] 2026-01-18 17:13:35,123 app.prompts get_github_data:34 - Error reading data from GitHub: ...
```

### Agregar Logs Propios:
```python
import logging

logger = logging.getLogger(__name__)

# En una vista
logger.info(f"User {request.user} accessed /admin/")
logger.warning(f"Form validation failed: {form.errors}")
logger.error(f"Database connection failed: {e}", exc_info=True)
```

---

## 🔒 SETTINGS POR ENTORNO

### Ver Configuración Actual:
```bash
python -c "
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'DATABASE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
"
```

### Cambiar Entre Entornos:
```bash
# Development
python manage.py runserver

# Production (local test)
DJANGO_ENV=production python manage.py check

# Testing
DJANGO_ENV=testing python manage.py test
```

---

## 🧪 TESTING CON VALIDACIONES

### Probar Validaciones:
```bash
python manage.py shell << 'EOF'
from app.landing.models import Skill
from django.core.exceptions import ValidationError

# Test válido
skill = Skill(name='Python', score=85)
skill.full_clean()  # ✅ No raise
skill.save()

# Test inválido
try:
    skill = Skill(name='JavaScript', score=150)
    skill.full_clean()  # ❌ Raises ValidationError
except ValidationError as e:
    print(f"Validación correcta: {e.message_dict}")
EOF
```

---

## 📱 ADMIN - CAMBIOS VISIBLES

### Antes de esta revisión:
```
Listado de Projects: HTML completo en descripción (lento)
Listado de Skills: No había score editable
Listado de Products: Margen no visible
```

### Después:
```
Listado de Projects: "Lorem ipsum dolor sit..." + Preview en edición ⚡
Listado de Skills: Editable inline, ordenado por score 📊
Listado de Products: Margen visible, status editable 💰
```

### Acceder:
```
http://127.0.0.1:8000/admin/
Usuario: tu superuser
Contraseña: tu password
```

---

## 🚨 TROUBLESHOOTING

### "No modulo app.config.settings":
```bash
# Verificar que no hay conflicto de archivos
ls -la app/config/
# Debe haber: settings/ (carpeta), logging_config.py
# NO debe haber: settings.py (archivo - fue renombrado a .bak)
```

### "ValidationError en admin":
```bash
# Normal, significa que la validación funciona
# Revisar el mensaje de error y corregir los datos
```

### "Logging no funciona":
```bash
# Crear directorio logs
mkdir -p app/logs

# Verificar permisos
ls -la app/logs/
```

### Settings sigue siendo monolítico:
```bash
# Asegurar que DJANGO_SETTINGS_MODULE apunta a paquete, no archivo:
# En manage.py, debe ser: 'app.config.settings' (sin .py)
```

---

## 📞 REFERENCIA RÁPIDA

| Tarea | Comando |
|-------|---------|
| Ejecutar dev | `python manage.py runserver` |
| Admin | `http://127.0.0.1:8000/admin/` |
| Migrar | `python manage.py migrate` |
| Tests | `DJANGO_ENV=testing python manage.py test` |
| Shell | `python manage.py shell` |
| Crear user | `python manage.py createsuperuser` |
| Ver logs | `tail -f app/logs/django.log` |
| Type check | `mypy app/` |

---

## ✅ CHECKLIST DE USO

- [ ] Ejecutar `python manage.py check` sin errores
- [ ] Acceder a admin y ver cambios UI
- [ ] Intentar guardar Skill con score > 100 (debe fallar)
- [ ] Probar type hints en IDE (ctrl+click en functions)
- [ ] Verificar logs en `app/logs/django.log`
- [ ] Probar diferentes entornos (DJANGO_ENV)

---

**¿Preguntas? Ver documentación:**
- [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) - Overview completo
- [REVISION_ARQUITECTONICA.md](REVISION_ARQUITECTONICA.md) - Detalles técnicos
- [OPCIONES_IMPLEMENTADAS.md](OPCIONES_IMPLEMENTADAS.md) - Cambios específicos
