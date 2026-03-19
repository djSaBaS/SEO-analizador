# src/info.md

Contiene el código fuente principal del auditor SEO.

## Módulos principales
- `main.py`: punto de entrada del CLI.
- `seo_auditor/config.py`: carga segura de configuración.
- `seo_auditor/models.py`: estructuras tipadas del dominio.
- `seo_auditor/utils.py`: utilidades comunes y validaciones.
- `seo_auditor/fetcher.py`: descarga y parseo de sitemaps y páginas.
- `seo_auditor/analyzer.py`: análisis SEO técnico y on-page.
- `seo_auditor/reporters.py`: exportación a JSON, Excel, Word y PDF.
- `seo_auditor/gemini_client.py`: enriquecimiento opcional con IA.
