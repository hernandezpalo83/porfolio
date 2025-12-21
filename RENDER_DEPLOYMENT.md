# 🚀 Deployment en Render.com

Este documento proporciona instrucciones completas para desplegar la aplicación Django Portfolio en Render.com.

## 📋 Requisitos Previos

- Cuenta en [Render.com](https://render.com)
- Repositorio en GitHub conectado
- Python 3.12 instalado localmente (para exportar datos)
- Git configurado

## 🔧 Paso 1: Preparación en Render.com

### 1.1 Crear un Web Service

1. Ve a [https://dashboard.render.com](https://dashboard.render.com)
2. Haz clic en **New +** → **Web Service**
3. Conecta tu repositorio GitHub
4. Selecciona el repositorio del portfolio

### 1.2 Configurar el Web Service

**Settings básicos:**
- **Name**: `portfolio`
- **Region**: Selecciona más cercano a tus usuarios (ej: Frankfurt)
- **Runtime**: Python 3
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && cd app && python manage.py collectstatic --noinput
  ```
- **Start Command**: 
  ```bash
  gunicorn app.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
  ```

### 1.3 Configurar Base de Datos PostgreSQL

1. En tu Web Service, ve a **Environment**
2. Haz clic en **Add Database**
3. Selecciona **PostgreSQL**
4. Acepta los valores por defecto (o personaliza si es necesario)

Render creará automáticamente una variable `DATABASE_URL`.

### 1.4 Variables de Entorno

En **Environment**, agrega estas variables:

```
SECRET_KEY = tu_django_secret_key_aqui
DEBUG = false
ALLOWED_HOSTS = portfolio.onrender.com,www.portfolio.onrender.com,localhost
DJANGO_SETTINGS_MODULE = app.settings
```

**Importante**: 
- Genera una `SECRET_KEY` segura: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- **NO** uses DEBUG=true en producción

### 1.5 Discos de Almacenamiento (opcional)

Para guardar fotos y datos:

1. Ve a **Disks**
2. Haz clic en **Add Disk**
3. **Mount Path**: `/data`
4. **Size**: 1GB (o lo que necesites)

## 📤 Paso 2: Exportar Datos Locales

Antes de hacer deploy, exporta tu base de datos SQLite:

```bash
cd /Users/hernandezpalo/Documents/Javi/Desarrollo/Django/porfolio
./deploy-render.sh export
```

Esto creará:
- `datos_full.json` - JSON con todos tus datos
- `datos_full.json.gz` - Versión comprimida

## 🚀 Paso 3: Hacer Push a GitHub

```bash
cd /Users/hernandezpalo/Documents/Javi/Desarrollo/Django/porfolio

# Agregar todos los cambios
git add -A

# Hacer commit
git commit -m "Migrar a Render.com - eliminar Fly.io"

# Push a main
git push origin main
```

Render monitorea tu rama `main` y automáticamente:
1. Detecta los cambios
2. Inicia un nuevo deployment
3. Ejecuta el build command
4. Ejecuta las migraciones (si las agregamos)
5. Inicia la aplicación

## 📊 Paso 4: Migrar Datos (Después del primer deploy)

Una vez que Render tenga tu app corriendo:

### Opción A: Via Render Shell (Recomendado)

1. Ve a tu Web Service en Render Dashboard
2. Haz clic en **Shell** (esquina superior derecha)
3. En la terminal que se abre:
   ```bash
   cd /app
   python manage.py migrate
   python manage.py shell < /dev/stdin <<'EOF'
   from django.contrib.auth.models import User
   User.objects.create_superuser('admin', 'admin@example.com', 'tu_password_aqui')
   EOF
   ```
4. Sube tu archivo `datos_full.json`:
   ```bash
   # En tu máquina local, desde la terminal de Render Shell:
   # Haz upload del archivo
   ```
5. Carga los datos:
   ```bash
   python manage.py loaddata datos_full.json --verbosity 2
   ```

### Opción B: Via Script Local

Si configuraste SSH en Render:

```bash
cd /Users/hernandezpalo/Documents/Javi/Desarrollo/Django/porfolio
./deploy-render.sh migrate
```

### Opción C: Manual

```bash
# Exportar datos
./deploy-render.sh export

# Luego manualmente:
# 1. Sube datos_full.json a Render via Web Console
# 2. Ejecuta loaddata en Render Shell
```

## 🔄 Actualizar la Aplicación (Después del Primer Deploy)

Cada vez que hagas cambios:

```bash
# 1. Cambios locales
nano app/settings.py
# ... edita lo que necesites ...

# 2. Agrega cambios a Git
git add app/settings.py

# 3. Commit
git commit -m "Descripción de cambios"

# 4. Push (Render automáticamente hace deploy)
git push origin main

# 5. Monitorea en Render Dashboard → Logs
```

## 🗄️ Base de Datos

### Conectarse a la BD en Render

```bash
# Obtener DATABASE_URL de tu Web Service
# Luego:
psql <DATABASE_URL>
```

### Hacer Backup de la BD

```bash
./deploy-render.sh backup
```

### Restaurar BD desde Backup

```bash
psql <DATABASE_URL> < backup_20231221_153000.sql
```

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app'"

Causa: Dockerfile no está en la raíz correcta
Solución: Verifica que `Dockerfile` está en `/Users/hernandezpalo/Documents/Javi/Desarrollo/Django/porfolio/`

### Error: "Database error"

1. Ve a Render Dashboard → tu Web Service
2. Haz clic en **Shell**
3. Ejecuta: `python manage.py migrate`

### Error: "Static files not found"

Solución: El comando collectstatic debería ejecutarse:
```bash
cd /app && python manage.py collectstatic --noinput --clear
```

### Error: "ALLOWED_HOSTS"

Solución: Actualiza la variable de entorno `ALLOWED_HOSTS` en Render Dashboard con tu dominio actual.

## 📱 URL de tu Aplicación

Una vez desplegado, tu app estará en:
- `https://portfolio.onrender.com` (por defecto)
- O el dominio personalizado que configures

## 💡 Buenas Prácticas

1. **Siempre** exporta datos antes de grandes cambios
2. Mantén `DEBUG = false` en producción
3. Usa variables de entorno para datos sensibles
4. Haz backups regularmente
5. Monitorea los logs en Render
6. Prueba localmente antes de hacer push

## 🔐 Seguridad

**Cambiar contraseña del superuser:**

En Render Shell:
```bash
python manage.py changepassword admin
```

**Generar nueva SECRET_KEY:**

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Luego actualiza en Render Dashboard → Environment.

## 📞 Soporte

- Documentación de Render: https://render.com/docs
- Comunidad: https://render.com/community
- Documentación de Django: https://docs.djangoproject.com

---

**Última actualización**: 21 de Diciembre de 2025
