# src/info.md

Contiene el código fuente principal del auditor SEO.

## Módulos principales
- `main.py`: punto de entrada del CLI.
- `seo_auditor/config.py`: carga segura de configuración.
- `seo_auditor/models.py`: modelos tipados con metadatos de cliente, fecha y gestor.
- `seo_auditor/utils.py`: validación, normalización y utilidades de fecha/slug de dominio.
- `seo_auditor/fetcher.py`: descarga y parseo de sitemaps y páginas.
- `seo_auditor/analyzer.py`: análisis SEO y clasificación automática de incidencias.
- `seo_auditor/reporters.py`: exportación profesional a JSON, Excel, Word, PDF y Markdown IA con maquetación corporativa y hoja auxiliar de dashboard.
- `seo_auditor/gemini_client.py`: generación de resumen IA optimizado en tokens.
