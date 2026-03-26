# src/info.md

Contiene el código fuente principal del auditor SEO.

## Módulos principales
- `main.py`: punto de entrada del CLI.
- `seo_auditor/config.py`: carga segura de configuración (Gemini + PageSpeed + límites).
- `seo_auditor/config.py`: carga segura de configuración (Gemini + PageSpeed + límites + timeout/reintentos).
- `seo_auditor/models.py`: modelos tipados de auditoría técnica, rendimiento y metadatos de fuentes activas.
- `seo_auditor/utils.py`: validación, normalización y utilidades de fecha/slug de dominio.
- `seo_auditor/fetcher.py`: descarga y parseo de sitemaps y páginas.
- `seo_auditor/analyzer.py`: análisis SEO y clasificación automática de incidencias.
- `seo_auditor/pagespeed.py`: integración con API pública de PageSpeed Insights y separación de laboratorio/campo.
- `seo_auditor/cache.py`: caché local con TTL e invalidación para IA y PageSpeed.
- `seo_auditor/analyzer.py`: análisis SEO por URL con barra de progreso visible durante la auditoría técnica.
- `seo_auditor/reporters.py`: exportación profesional a JSON, Excel, Word, PDF, HTML y Markdown IA, con separación entre capa técnica y capa ejecutiva (pestaña `KPIs`, `Dashboard` analítico, incidencias agrupadas, quick wins por URL, gestión de indexación, sección de comportamiento y conversión, páginas prioritarias y cruce GSC+GA4).
- `seo_auditor/gemini_client.py`: generación de resumen IA optimizado en tokens y validación de conectividad con `--testia`, usando plantilla editable `prompts/` (modular por modo con fallback a `informe_general.txt`) con fallback idéntico y control explícito de coherencia contextual (`contexto_control`) para evitar contradicciones con GSC.

- `seo_auditor/indexacion.py`: análisis de indexación y rastreo con robots/sitemap usando advertools, más clasificación inteligente de URLs (INDEXABLE/REVISAR/NO_INDEXAR) combinando señales de URL, contenido, SEO y GSC.

- `seo_auditor/gsc.py`: integración opcional con Google Search Console (service account), consultas por página/query y degradación elegante.

- `seo_auditor/ga4.py`: integración opcional con Google Analytics 4 para métricas por página y resumen agregado.
- `seo_auditor/ga4_premium.py`: generador del modo `--modo informe-ga4` con consultas avanzadas por secciones, gráficos Plotly y exportación premium a HTML/PDF/Excel.

- `seo_auditor/cli.py`: CLI principal con modo dedicado `--modo informe-ga4`, soporte de comparación (`--comparar`), filtro local (`--provincia`) y nombre explícito de cliente (`--cliente`).
