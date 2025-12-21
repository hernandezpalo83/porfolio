# Configuración de Fly.io para Portfolio

## Estado actual

- **App Fly:** `porfolio-polished-water-5224`
- **URL Fly (directa):** https://porfolio-polished-water-5224.fly.dev
- **URL Final (custom domain):** https://porfolio.hernandezpalo.es
- **Región:** Amsterdam (ams) — baja latencia a España
- **Volumen persistente:** `/data` → `porfolio_data` (1 GB)
- **BD:** SQLite en `/data/db.sqlite3`

---

## 1. Configuración DNS (IMPORTANTE)

Elige **UNA** de las tres opciones para configurar tu dominio en tu proveedor DNS (ej. Route53, Namecheap, GoDaddy, etc.):

### Opción A: CNAME (Más simple — recomendado para DNS simple)

Crea un registro CNAME apuntando `porfolio` a la URL de Fly:

| Tipo  | Nombre         | Valor                                     |
|-------|----------------|-------------------------------------------|
| CNAME | porfolio       | j5ed2l5.porfolio-polished-water-5224.fly.dev |

**Resultado:** `porfolio.hernandezpalo.es` → `j5ed2l5.porfolio-polished-water-5224.fly.dev` → IP de Fly

---

### Opción B: A + AAAA (Conexión directa — más rápido)

Crea dos registros apuntando directamente a los IPs de Fly:

| Tipo | Nombre   | Valor             |
|------|----------|-------------------|
| A    | porfolio | 66.241.124.211    |
| AAAA | porfolio | 2a09:8280:1::bd:4741:0 |

**Resultado:** Conexión directa sin intermediarios.

---

### Opción C: External Proxy Setup (Si usas un proxy/CDN)

Solo si tu dominio está detrás de un proxy o CDN:

| Tipo | Nombre   | Valor             |
|------|----------|-------------------|
| AAAA | porfolio | 2a09:8280:1::bd:4741:0 |

---

## 2. Verificar la configuración DNS

Una vez hayas configurado tu DNS (puede tomar 5-30 minutos), verifica el progreso:

```bash
flyctl certs check porfolio.hernandezpalo.es --app porfolio-polished-water-5224
```

Esperado:
```
Certificate details
  Hostname:            porfolio.hernandezpalo.es
  DNS validated:       Yes
  Certificate issued:  Yes
  Issue date:          2025-12-21
  Expiration date:     2026-03-21
```

---

## 3. Desplegar actualizaciones

### Script automático (recomendado)

```bash
cd /Users/hernandezpalo/Documents/Javi/Desarrollo/Django/porfolio/app
./deploy.sh "Mensaje de actualización (opcional)"
```

Ejemplo:
```bash
./deploy.sh "Actualizar galería de imágenes"
```

### Comando manual (sin script)

```bash
flyctl deploy --app porfolio-polished-water-5224 --remote-only
```

---

## 4. Ver logs en tiempo real

```bash
flyctl logs --app porfolio-polished-water-5224 -f
```

---

## 5. Acceder a la shell de Django

```bash
flyctl ssh console --app porfolio-polished-water-5224
python manage.py shell
```

---

## 6. Secrets configurados

Los siguientes secrets están guardados en Fly:

- `SECRET_KEY` — Clave secreta de Django (regenerada en despliegue)
- `DEBUG` — `False` (producción)
- `DB_PATH` — `/data/db.sqlite3` (ubicación de la BD persistente)
- `ALLOWED_HOSTS` — `porfolio-polished-water-5224.fly.dev,porfolio.hernandezpalo.es`

Para actualizar un secret:
```bash
flyctl secrets set VARIABLE_NAME="valor" --app porfolio-polished-water-5224
```

Para listar:
```bash
flyctl secrets list --app porfolio-polished-water-5224
```

---

## 7. Troubleshooting

### El dominio no resuelve a Fly

1. Verifica que el DNS está propagado: `nslookup porfolio.hernandezpalo.es`
2. Si ves tu proveedor DNS anterior, espera 5-30 min y reintenta.

### Error 502 Bad Gateway

1. Revisa los logs: `flyctl logs --app porfolio-polished-water-5224 -f`
2. Reinicia la máquina: `flyctl machines restart <machine-id>`

### Base de datos vacía después del despliegue

Asegúrate de que el volumen está montado correctamente en `/data`:

```bash
flyctl volumes list --app porfolio-polished-water-5224
```

Debe mostrar `porfolio_data` con status `created`.

---

## 8. Archivos principales

- [deploy.sh](./deploy.sh) — Script de despliegue automático
- [fly.toml](./fly.toml) — Configuración de Fly
- [Dockerfile](./Dockerfile) — Imagen Docker
- [app/settings.py](./app/settings.py) — Configuración de Django (con CSRF_TRUSTED_ORIGINS)

---

## Notas finales

- El certificado SSL se renueva automáticamente cada 3 meses.
- El volumen está en la región `ams` (Amsterdam), así que no se puede reubicar sin migración.
- Los despliegues son rápidos (build remoto ~50 segundos).
- Para más info: https://fly.io/docs/
