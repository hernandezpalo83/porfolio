# Informe de Compatibilidad Safari y Webkit - v2.2.1

## 🎯 Objetivo
Solucionar problemas críticos de visualización en navegadores Safari (especialmente en iOS) detectados tras el rediseño de la versión 2.2.0.

## 🛠️ Arreglos Técnicos

### 1. Fondo de Intro (Safari Mobile Bug)
- **Problema**: La imagen de fondo del `#intro` desaparecía en iPhone/iPad debido a una incompatibilidad de Safari con `background-attachment: fixed`.
- **Solución**: Se ha implementado un media-query específico para dispositivos táctiles/móviles que cambia el comportamiento a `scroll` (valor por defecto) para asegurar que la imagen se renderice correctamente.
- **Mejora**: Se ha cambiado `background-size: contain` a `cover` para que la imagen hero rellene mejor la pantalla.

### 2. Grid de Formación (Webkit Flexbox)
- **Problema**: Las tarjetas de educación no mantenían su estructura de 2 columnas o se veían desalineadas en Safari.
- **Solución**:
  - Se han añadido prefijos `-webkit-flex` y `-webkit-flex-direction`.
  - Se ha especificado `width: 100%` en las tarjetas interiores para forzar que rellenen su contenedor flex.
  - Se han optimizado los cálculos de `flex-basis` para manejar mejor los `gap` en el motor de renderizado Webkit.

## 🧱 Archivos Modificados
- `app/landing/static/landing/css/main.css`
- `app/landing/static/landing/css/centering_fixes.css`
- `app/landing/static/landing/css/components.css`

---
*Documento generado por Antigravity - Enero 2026*
