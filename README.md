# Auditor SEO Pro con Python + Gemini + PageSpeed

Herramienta de auditoría SEO técnica y ejecutiva para agencia, con exportación profesional a JSON, Excel, Word, PDF y Markdown IA.

## Objetivo
- Analizar sitemaps XML.
- Auditar URLs y señales SEO on-page.
- Integrar PageSpeed Insights (móvil/escritorio) con control de alcance.
- Cachear resultados costosos (PageSpeed e IA) con TTL configurable.
- Clasificar incidencias automáticamente por severidad, área, impacto, esfuerzo y prioridad.
- Diferenciar capa técnica (detalle) y capa ejecutiva (incidencias agrupadas).
- Generar entregables orientados a cliente final sin markdown crudo en DOCX/PDF.
- Exportar adicionalmente un informe HTML reutilizable.
- Reducir consumo de tokens en IA mediante contexto agregado.

## Requisitos
- Python 3.11 o superior.
- Conexión a internet para auditar webs y para usar APIs.
- Variables de entorno opcionales:
  - `GEMINI_API_KEY`
  - `GEMINI_MODEL` (opcional, por defecto `gemini-2.0-flash`)
  - `PAGESPEED_API_KEY`
  - `HTTP_TIMEOUT` (opcional)
  - `MAX_URLS` (opcional)
  - `MAX_PAGESPEED_URLS` (opcional)
  - `PAGESPEED_TIMEOUT` (opcional, recomendado `45`)
  - `PAGESPEED_REINTENTOS` (opcional, recomendado `2`)
  - `CACHE_TTL_SEGUNDOS` (opcional, recomendado `21600`)

## Dónde configurar las API keys
- Debes definir las claves en tu archivo `.env` (o en variables de entorno del sistema), **no** en `config.py`.
- `config.py` solo carga y valida valores de entorno; por eso puede verse vacío y aun así funcionar si la variable existe en tu entorno.
- Ejemplo mínimo en `.env`:
  - `GEMINI_API_KEY=tu_clave`
  - `PAGESPEED_API_KEY=tu_clave`
  - `PAGESPEED_TIMEOUT=45`
  - `PAGESPEED_REINTENTOS=2`

## Ejecución básica
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap_index.xml --output ./salidas
```

## Ejecución con IA
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap_index.xml --output ./salidas --usar-ia
```

## Prueba mínima de IA (`--testia`)
```bash
python src/main.py --testia
python src/main.py --testia --modelo-ia gemini-2.0-flash
```

## Parámetros CLI clave
- `--gestor "Nombre Apellidos"`: define gestor del informe.
- `--max-muestras-ia 15`: limita muestras agregadas enviadas a Gemini.
- `--modo-rapido`: limita la auditoría técnica a una muestra ligera para demos.
- `--cache-ttl N`: define TTL de caché local para IA y PageSpeed.
- `--invalidar-cache`: elimina la caché local antes de ejecutar.
- `--pagepsi <url>`: analiza solo esa URL en PageSpeed (mobile+desktop).
- `--pagepsi-list <archivo>`: analiza lista de URLs (una por línea).
- `--max-pagepsi-urls N`: limita URLs de PageSpeed para esa ejecución.
- `--pagepsi-timeout N`: timeout de PageSpeed para esa ejecución.
- `--pagepsi-reintentos N`: reintentos de PageSpeed para esa ejecución.

## Comportamiento de PageSpeed
- Si existe `PAGESPEED_API_KEY` y no se indica nada, analiza solo la HOME.
- La HOME se detecta desde dominio/sitemap.
- Si se indica `--pagepsi`, solo analiza esa URL.
- Si se indica `--pagepsi-list`, usa esa lista con límite.
- Siempre informa en consola qué URL/estrategia se está analizando.

## Estructura de salida
```text
<output>/<slug_dominio>/<YYYY-MM-DD>/
```

## Canonical: nueva lógica de coherencia
- Se normalizan esquema, host, puertos por defecto, slash final, query ordenada y fragmento.
- Nuevos estados:
  - `diferencia menor normalizable` (baja severidad)
  - `canonical potencialmente incoherente` (media severidad)
  - `canonical realmente incoherente` (alta severidad)
- Si la diferencia es solo slash final y la URL auditada responde 200, no escala automáticamente a alta severidad.

## Capa ejecutiva vs capa técnica
- Excel y anexo técnico mantienen el detalle de incidencias individuales.
- Word/PDF/HTML añaden una capa ejecutiva con:
  - quick wins deduplicados y estructurados
  - incidencias agrupadas por familia de problema
  - presentación de rendimiento en formato más legible por métrica
- El score incluye desglose por bloques para interpretación de negocio.
- Quick Wins se agrupa por URL y se presenta en tarjetas (Word/PDF/HTML) con problemas, acciones, impacto y esfuerzo.
- Roadmap incluye fallback obligatorio de fase de medio plazo para evitar bloques vacíos.

## Calidad documental
- Jerarquía fija del informe: portada, resumen, KPIs, hallazgos, quick wins, acciones, rendimiento, roadmap y anexo.
- Capa intermedia IA→secciones para evitar markdown crudo en Word/PDF.
- Anexo técnico generado solo desde datos estructurados.
- La IA no debe inventar fuentes no activas.

## Ejecutar tests
```bash
pytest -q
```


## Novedades de auditoría avanzada (v0.6.0)
- Integración de `trafilatura` para extraer contenido limpio y calcular palabras, densidad, ratio texto/HTML, thin content y duplicidad aproximada por hash.
- Integración de `advertools` para análisis base de `robots.txt` y coherencia sitemap vs reglas Disallow.
- Nueva sección ejecutiva **Indexación y rastreo** en Word/PDF/HTML.
- Nueva hoja **Contenido** en Excel con métricas accionables por URL (palabras, calidad, thin content, headings, imágenes sin alt).
- Compatibilidad CLI: si no se indica `--output`, se usa `./salidas` automáticamente.
