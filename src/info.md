# src/info.md

Contiene el código fuente principal del auditor SEO.

## Módulos principales
- `main.py`: punto de entrada del CLI.
- `seo_auditor/config.py`: carga segura de configuración (Gemini + PageSpeed + límites).
- `seo_auditor/models.py`: modelos tipados de auditoría técnica, rendimiento y metadatos de fuentes activas.
- `seo_auditor/utils.py`: validación, normalización y utilidades de fecha/slug de dominio.
- `seo_auditor/fetcher.py`: descarga y parseo de sitemaps y páginas.
- `seo_auditor/analyzer.py`: análisis SEO y clasificación automática de incidencias.
- `seo_auditor/pagespeed.py`: integración con API pública de PageSpeed Insights y separación de laboratorio/campo.
- `seo_auditor/reporters.py`: exportación profesional a JSON, Excel, Word, PDF y Markdown IA, con jerarquía documental estable y sin markdown crudo en entregables finales.
- `seo_auditor/gemini_client.py`: generación de resumen IA optimizado en tokens y validación de conectividad con `--testia`.
