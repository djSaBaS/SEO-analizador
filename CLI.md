# CLI.md

Guía completa de uso de la línea de comandos del proyecto.

## Comando base
```bash
python src/main.py [opciones]
```

---

## 1) Auditoría SEO completa

### 1.1 Ejecución mínima
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas
```
Qué hace:
- Extrae URLs del sitemap.
- Audita SEO técnico y contenido.
- Exporta JSON, Excel, Word, PDF, HTML y Markdown.

### 1.2 Sin `--output` (usa valor por defecto)
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml
```
Qué hace:
- Ejecuta igual que el caso mínimo.
- Guarda salida en `./salidas`.

### 1.3 Con gestor personalizado
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --gestor "Ana Pérez"
```
Qué hace:
- Inserta el nombre del gestor en metadatos/cabeceras de informes.

### 1.4 Auditoría rápida
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --modo-rapido
```
Qué hace:
- Limita el volumen de URLs auditadas para acelerar ejecución.

---

## 2) IA (Gemini)

### 2.1 Auditoría + IA (modo completo)
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --usar-ia --modo completo
```
Qué hace:
- Ejecuta auditoría completa.
- Genera narrativa IA con prompt `completo`.

### 2.2 IA modo resumen ejecutivo
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --usar-ia --modo resumen
```
Qué hace:
- Prioriza salida ejecutiva resumida con IA.

### 2.3 IA modo quick wins
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --usar-ia --modo quickwins
```
Qué hace:
- Orienta el texto IA a acciones rápidas de alto impacto.

### 2.4 IA modo enfoque GSC
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --usar-ia --modo gsc
```
Qué hace:
- Enfatiza oportunidades de visibilidad orgánica basadas en Search Console (si está activo).

### 2.5 IA modo roadmap
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --usar-ia --modo roadmap
```
Qué hace:
- Orienta narrativa a plan por fases.

### 2.6 Forzar modelo IA
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --usar-ia --modelo-ia gemini-2.5-flash
```
Qué hace:
- Sobrescribe el modelo configurado en entorno para esta ejecución.

### 2.7 Limitar muestras para IA
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --usar-ia --max-muestras-ia 8
```
Qué hace:
- Reduce datos enviados a IA para controlar coste/latencia.

### 2.8 Test de conectividad IA
```bash
python src/main.py --testia
python src/main.py --testia --modelo-ia gemini-2.5-flash
```
Qué hace:
- Verifica API/modelo de IA sin generar informes.

---

## 3) PageSpeed

### 3.1 Comportamiento por defecto (si existe API key)
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas
```
Qué hace:
- Ejecuta PageSpeed solo para HOME (mobile y desktop).

### 3.2 PageSpeed para URL única
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --pagepsi https://www.ejemplo.com/servicios
```
Qué hace:
- Analiza únicamente la URL indicada con PageSpeed.

### 3.3 PageSpeed desde lista de archivo
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --pagepsi-list ./urls_pagespeed.txt
```
Qué hace:
- Carga URLs válidas desde archivo (una por línea).
- Si no encuentra URLs válidas, cae a HOME automáticamente.

### 3.4 Limitar URLs de lista
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --pagepsi-list ./urls_pagespeed.txt --max-pagepsi-urls 3
```
Qué hace:
- Limita la cantidad de URLs analizadas por PageSpeed.

### 3.5 Ajustar timeout y reintentos
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --pagepsi-timeout 60 --pagepsi-reintentos 1
```
Qué hace:
- Usa timeout/reintentos específicos para esta ejecución.

---

## 4) Caché

### 4.1 TTL de caché personalizado
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --cache-ttl 3600
```
Qué hace:
- Aplica TTL de 1 hora a caché de IA/PageSpeed en esta ejecución.

### 4.2 Invalidar caché antes de auditar
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --invalidar-cache
```
Qué hace:
- Elimina entradas cacheadas antes del análisis.

---

## 5) Google Search Console y GA4

### 5.1 Test de conectividad GSC
```bash
python src/main.py --testgsc
```
Qué hace:
- Verifica credenciales/permisos/rango de Search Console y finaliza.

### 5.2 Test de conectividad GA4
```bash
python src/main.py --testga
```
Qué hace:
- Verifica credenciales/permisos/rango de Analytics y finaliza.

### 5.3 Desactivar GSC en una ejecución puntual
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --noGSC
```
Qué hace:
- Omite Search Console aunque esté habilitado en entorno.

---

## 6) Fechas globales de análisis

### 6.1 Definir rango explícito
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --date-from 2026-02-01 --date-to 2026-02-28
```
Qué hace:
- Aplica ese rango temporal a fuentes que lo soportan (GSC/GA4 y extensiones futuras).

### 6.2 Sin rango explícito
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas
```
Qué hace:
- Usa automáticamente la ventana de últimos 28 días cerrados (hasta ayer).

---

## 7) Modo dedicado: informe GA4 premium

### 7.1 Ejecución básica
```bash
python src/main.py --modo informe-ga4 --output ./salidas
```
Qué hace:
- No ejecuta auditoría SEO completa.
- Genera informe premium de GA4 (HTML/PDF/Excel).

### 7.2 Con cliente, comparativa y provincia
```bash
python src/main.py --modo informe-ga4 --output ./salidas --cliente "Clínica Dental Sol" --comparar anio-anterior --provincia valencia --gestor "Ana Pérez"
```
Qué hace:
- Genera informe GA4 premium con portada personalizada.
- Compara contra año anterior.
- Enfatiza detalle local para provincia indicada.

### 7.3 Informe GA4 premium inferido desde sitemap
```bash
python src/main.py --modo informe-ga4 --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas
```
Qué hace:
- Si no se pasa `--cliente`, intenta inferir nombre desde el dominio del sitemap.

---

## 8) Compatibilidades e incompatibilidades

### No compatibles
- `--pagepsi` y `--pagepsi-list` en la misma ejecución.

### Reglas de validación importantes
- `--max-muestras-ia` debe ser > 0.
- `--max-pagepsi-urls` no puede ser negativo.
- `--pagepsi-timeout` no puede ser negativo.
- `--pagepsi-reintentos` debe ser `-1` o mayor.
- `--date-from` y `--date-to` deben enviarse juntos y en formato `YYYY-MM-DD`.

---

## 9) Ejemplo integral recomendado
```bash
python src/main.py \
  --sitemap https://www.ejemplo.com/sitemap_index.xml \
  --output ./salidas \
  --usar-ia \
  --modo quickwins \
  --pagepsi-list ./urls_pagespeed.txt \
  --max-pagepsi-urls 5 \
  --pagepsi-timeout 45 \
  --pagepsi-reintentos 2 \
  --cache-ttl 7200 \
  --date-from 2026-02-01 \
  --date-to 2026-02-28 \
  --gestor "Juan Antonio Sánchez Plaza"
```
Qué hace:
- Ejecuta auditoría completa con salida profesional.
- Añade narrativa IA enfocada a quick wins.
- Mide PageSpeed en lista acotada.
- Aplica rango temporal definido para fuentes autenticadas.
