# 🚀 Deploy en Render.com - Guía Rápida

## TL;DR (Demasiado Largo; Aquí Está Lo Importante)

```bash
# 1. Exportar datos
./deploy-render.sh export

# 2. Crear una app en Render.com (ver abajo)

# 3. Push a GitHub
git add -A
git commit -m "Migrar a Render.com"
git push origin main

# 4. Esperar deploy automático
# 5. Cargar datos en Render Shell
python manage.py shell < init_render_db.py
python manage.py loaddata datos_full.json
```

## ⚡ Pasos Rápidos

### 1️⃣ Preparar Datos Locales (2 min)

```bash
cd /Users/hernandezpalo/Documents/Javi/Desarrollo/Django/porfolio
./deploy-render.sh export
```

Esto crea `datos_full.json` con toda tu información.

### 2️⃣ Crear Web Service en Render (5 min)

1. Ve a https://dashboard.render.com
2. **New +** → **Web Service**
3. Conecta tu repositorio
4. Rellena:
   ```
   Name: portfolio
   Build Command: pip install -r requirements.txt && cd app && python manage.py collectstatic --noinput
   Start Command: gunicorn app.wsgi:application --bind 0.0.0.0:$PORT
   ```
5. Selecciona **PostgreSQL** → **Add Database** (Render lo hace automáticamente)
6. **Create Web Service**

### 3️⃣ Configurar Variables de Entorno (3 min)

En tu Web Service de Render → **Environment**:

```
SECRET_KEY=<genera_uno_nuevo>
DEBUG=false
ALLOWED_HOSTS=portfolio.onrender.com,localhost
```

Para generar SECRET_KEY:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4️⃣ Hacer Deploy (1 min)

```bash
cd /Users/hernandezpalo/Documents/Javi/Desarrollo/Django/porfolio
git add -A
git commit -m "Migrar a Render.com"
git push origin main
```

**Listo!** Render automáticamente detecta y hace deploy.

### 5️⃣ Migrar Datos (3 min)

Una vez que Render termine el deploy:

1. En tu Web Service → **Shell** (arriba a la derecha)
2. En la terminal que abre:
   ```bash
   cd /app
   python manage.py shell < init_render_db.py
   ```
3. Esto crea el superuser y ejecuta migraciones
4. Luego carga tus datos:
   ```bash
   python manage.py loaddata datos_full.json
   ```

## 📊 Archivos Creados

| Archivo | Propósito |
|---------|-----------|
| `render.yaml` | Configuración de Render |
| `Dockerfile` | Para Docker (si lo necesitas) |
| `deploy-render.sh` | Script de deploy/export/backup |
| `quickstart-render.sh` | Script rápido de inicio |
| `app/migrate_to_render.py` | Migración de datos avanzada |
| `app/init_render_db.py` | Inicialización automática de BD |
| `RENDER_DEPLOYMENT.md` | Guía completa y detallada |
| `.env.example` | Ejemplo de variables de entorno |

## 🆘 Problemas Comunes

**¿Cómo veo los logs?**
→ Web Service → Logs (pestaña)

**¿Mi app está 500?**
→ Mira los logs. Generalmente es porque falta migración o SECRET_KEY

**¿Cambiar contraseña del admin?**
```bash
# En Render Shell:
python manage.py changepassword admin
```

**¿Dónde está mi DB?**
→ Render crea una PostgreSQL automáticamente y genera DATABASE_URL

**¿Cómo hago backup?**
```bash
./deploy-render.sh backup
```

## 🔐 Lo MÁS Importante

⚠️ **NUNCA olvidar:**
- ✅ DEBUG = false en producción
- ✅ SECRET_KEY segura y única
- ✅ Cambiar contraseña del admin
- ✅ ALLOWED_HOSTS con tu dominio
- ✅ NO subir .env al repositorio

## 📚 Si Necesitas Más Detalles

Lee **RENDER_DEPLOYMENT.md** - tiene todo paso a paso.

## 🎯 Estado del Proyecto

✅ Fly.io eliminado  
✅ Render.com configurado  
✅ Scripts de migración listos  
✅ Listo para hacer deploy  

---

**¿Dudas?** Revisa RENDER_DEPLOYMENT.md o contáctame.

¡A desplegar! 🚀
