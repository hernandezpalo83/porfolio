# 📊 Analytics — Dashboard Privacy-First + Blog Trending

**Sistema completo de analítica implementado sin cookies, con tracking de vistas, países, dispositivos y trending de posts.**

---

## Visión General

`app.analytics` captura datos de tráfico en tiempo real sin usar cookies (privacy-first), alimentando tres dashboards:

1. **Analytics General** (`/private/analytics/`) — Tráfico global
2. **Blog Analytics** (`/private/analytics/blog/`) — Posts trending
3. **Post Detail** (`/private/analytics/post/<id>/`) — Detalle por post

---

## Modelos

### `PageView`
Cada vista de página registra:
- `path` — Ruta visitada
- `country` — País detectado desde IP
- `device` — Tipo (mobile/tablet/desktop)
- `referrer` — Origen del tráfico
- `scroll_depth` — Porcentaje scrolleado (0-100)
- `time_spent` — Segundos en la página
- `session_id` — Identificador de sesión (sin cookies)

**Índices**: `path + timestamp`, `session_id + timestamp`, `country + timestamp`

### `SessionTracker`
Agrupa `PageView` por sesión:
- `session_id` — Único por usuario
- `page_count` — Número de páginas visitadas
- `total_duration` — Segundos totales
- `is_bounce` — True si visitó solo 1 página

### `PostAnalytics`
Agregaciones diarias por post:
- `views_today`, `views_7d`, `views_30d`, `views_all_time`
- `bounce_rate` — Porcentaje de sesiones que rebotan
- `avg_scroll_depth` — Profundidad de lectura promedio
- `avg_time_spent` — Segundos promedio
- `unique_visitors_7d` — Sesiones únicas en 7 días
- `trending_score` — Score para ranking (0-100)

### `RelatedPostsCache`
Posts relacionados basados en tags compartidos:
- Calcula automáticamente con `manage.py update_analytics`
- Al menos 2 tags compartidos para ser relacionado

---

## Middleware

`AnalyticsTrackingMiddleware` captura cada request:

```python
# settings/base.py
MIDDLEWARE = [
    ...
    'app.analytics.middleware.AnalyticsTrackingMiddleware',
]
```

**Comportamiento**:
- Genera `session_id` único por usuario (sin cookies)
- Registra en `PageView` con: país, dispositivo, referrer, IP
- Actualiza o crea `SessionTracker` por sesión
- Excluye paths: `/admin/`, `/static/`, `/media/`, `/api/`, `/health/`

**Notas**:
- Privacy-first: solo detecta país anónimamente via ip-api.com
- Caché de 1000 IPs para evitar rate limits
- Compatible con proxies (X-Forwarded-For)

---

## Management Command

```bash
python manage.py update_analytics [--full]
```

Actualiza agregaciones:
- Calcula `views_7d`, `views_30d`, `bounce_rate` por post
- Calcula `trending_score` basado en: vistas (7d) + visitantes únicos - bounce rate
- Descubre posts relacionados por co-ocurrencia de tags
- `--full` recalcula desde cero (puede ser lento)

**Recomendación**: ejecutar diariamente vía Celery o cron:
```bash
0 3 * * * python manage.py update_analytics  # 3 AM diarios
```

---

## Dashboards (Vistas)

### 1. Analytics General
**Ruta**: `/private/analytics/`  
**Plantilla**: `analytics_dashboard.html`

**Métricas**:
- 📊 Vistas hoy / 7d / 30d
- 👥 Sesiones únicas (7d)
- 📉 Bounce rate (7d)
- Duración promedio (7d)

**Gráficos** (Chart.js):
- Línea: vistas diarias (30d)
- Doughnut: distribución por dispositivo
- Barra horizontal: top países
- Tabla: top páginas

### 2. Blog Analytics
**Ruta**: `/private/analytics/blog/`  
**Plantilla**: `blog_analytics_dashboard.html`

**Trending** (últimos 7 días):
- Posts con vistas > 0 en 7d
- Ordenados por `trending_score`
- Muestra score y vistas

**Top All-Time**:
- Tabla con todas las métricas
- Bounce rate con badges (color rojo/naranja/verde)
- Links a detalle de cada post

### 3. Post Detail
**Ruta**: `/private/analytics/post/<id>/`  
**Plantilla**: `post_detail_analytics.html`

**Métricas principales**:
- Vistas (7d)
- Bounce rate
- Scroll depth avg
- Tiempo promedio

**Gráfico**: línea de vistas diarias (30d)

**Posts relacionados**: basados en tags compartidos

**Vistas recientes** (últimas 100):
- Tabla con país, dispositivo, referrer, scroll depth, hora

---

## APIs JSON (Datos para Dashboards)

| Endpoint | Retorna | Uso |
|---|---|---|
| `/private/analytics/api/views-by-day/` | Vistas diarias (30d) | Gráfico línea |
| `/private/analytics/api/devices-distribution/` | Vistas por dispositivo | Gráfico doughnut |
| `/private/analytics/api/countries-distribution/` | Top 15 países | Gráfico barra |
| `/private/analytics/api/top-pages/` | Top 10 páginas | Lista en dashboard |
| `/private/analytics/api/referrers/` | Top 10 referrers | Análisis de tráfico |
| `/private/analytics/api/post/<id>/views-by-day/` | Vistas diarias de post | Gráfico post detail |

Todas requieren autenticación (`@login_required`).

---

## Cálculo de Trending Score

```
base_score = min(views_7d / 10, 40)           # Máx 40
visitor_score = min(unique_visitors_7d / 5, 30)  # Máx 30
bounce_penalty = (bounce_rate / 100) * 30    # Hasta -30
trending_score = base_score + visitor_score - bounce_penalty
# Clampear a [0, 100]
```

**Ejemplo**:
- 50 vistas 7d → 40 base
- 20 visitantes únicos → 30 visitor
- 40% bounce → -12 penalty
- **Score = 40 + 30 - 12 = 58**

---

## Configuración (Pasos de Setup)

### 1. Base de datos (ya hecha)
```bash
python manage.py migrate analytics
```

### 2. Middleware activo
```python
# settings/base.py → ya incluido
MIDDLEWARE = [..., 'app.analytics.middleware.AnalyticsTrackingMiddleware']
```

### 3. URLs registradas
```python
# config/urls.py → ya incluido
path('private/analytics/', include('app.analytics.urls', namespace='analytics'))
```

### 4. Ejecutar agregaciones (primer run)
```bash
python manage.py update_analytics
```

### 5. Programar ejecución diaria (Celery)
```python
# celery_tasks.py (opcional)
@periodic_task(run_every=crontab(hour=3, minute=0))
def update_analytics_task():
    from django.core.management import call_command
    call_command('update_analytics')
```

---

## Notas de Seguridad

- ✅ **Sin cookies**: la sesión se genera por UUID, sin persistencia
- ✅ **Sin datos sensibles**: solo country, device, path, referrer
- ✅ **GDPR-friendly**: se pueden borrar datos viejos sin problema
- ✅ **Rate limiting**: caché de 1000 IPs evita overload a ip-api.com
- ⚠️ **ip-api.com**: requiere conexión external (puede fallar, defaults a 'XX')

---

## Extensiones Futuras

- **Heatmaps**: JavaScript para capturar clicks/movimientos del mouse
- **Conversión funnels**: trackear flujos de usuario
- **Exportar datos**: CSV/PDF con reportes mensuales
- **Superset**: integración para dashboards avanzados con PostgreSQL
- **Notificaciones**: alertas cuando un post trending alcanza X vistas

---

## Troubleshooting

### Las vistas no se registran
1. Verificar que middleware esté activo en settings
2. Asegurar que las URLs tengan `name=` (path debe ser válida)
3. Revisar logs: `logger.error()` en middleware

### IP-API offline
- Fallback a país 'XX' (desconocido)
- Datos se guardan igual, solo sin país

### PostAnalytics vacío
- Ejecutar: `python manage.py update_analytics`
- Verificar que existan `Post` en blog

