# Auditor SEO Pro con Python + Gemini + PageSpeed

Herramienta de auditoría SEO técnica y ejecutiva para agencia, con exportación profesional a JSON, Excel, Word, PDF y Markdown IA.

## Objetivo
- Analizar sitemaps XML.
- Auditar URLs y señales SEO on-page.
- Integrar PageSpeed Insights (móvil/escritorio) con control de alcance.
- Clasificar incidencias automáticamente por severidad, área, impacto, esfuerzo y prioridad.
- Generar entregables orientados a cliente final sin markdown crudo en DOCX/PDF.
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
- `--pagepsi <url>`: analiza solo esa URL en PageSpeed (mobile+desktop).
- `--pagepsi-list <archivo>`: analiza lista de URLs (una por línea).
- `--max-pagepsi-urls N`: limita URLs de PageSpeed para esa ejecución.

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

## Calidad documental
- Jerarquía fija del informe: portada, resumen, KPIs, hallazgos, quick wins, acciones, rendimiento, roadmap y anexo.
- Capa intermedia IA→secciones para evitar markdown crudo en Word/PDF.
- Anexo técnico generado solo desde datos estructurados.
- La IA no debe inventar fuentes no activas.

## Ejecutar tests
```bash
pytest -q
```
