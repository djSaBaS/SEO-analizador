# src/info.md

Código fuente principal del proyecto.

## Estructura clave
- `main.py`: punto de entrada del CLI.
- `seo_auditor/cli.py`: orquestación principal, parseo de argumentos, perfiles de generación compuesta (`--generar-todo` / `--modo entrega-completa`), modos de prueba y modo dedicado `informe-ga4`.
- `seo_auditor/config.py`: carga/validación de configuración desde variables de entorno.
- `seo_auditor/models.py`: modelos de datos tipados para resultados técnicos, rendimiento, GSC y GA4.

## Módulos funcionales
- `seo_auditor/fetcher.py`: lectura y parseo de sitemaps.
- `seo_auditor/analyzer.py`: auditoría SEO técnica y de contenido por URL.
- `seo_auditor/pagespeed.py`: integración con Google PageSpeed Insights.
- `seo_auditor/indexacion.py`: reglas de indexación/rastreo y clasificación de URLs.
- `seo_auditor/gsc.py`: integración opcional con Google Search Console.
- `seo_auditor/ga4.py`: integración opcional con Google Analytics 4.
- `seo_auditor/ga4_premium.py`: generación del informe dedicado GA4 premium (HTML/PDF/Excel).
- `seo_auditor/gemini_client.py`: integración IA para narrativa y validación de conectividad.
- `seo_auditor/cache.py`: caché local con TTL e invalidación.
- `seo_auditor/utils.py`: utilidades generales (fechas, URLs, slug, progreso).
- `seo_auditor/reporters/`: paquete modular de exportación documental; `core.py` concentra lógica común y cada exportador vive en su propio módulo (`exportador_word.py`, `exportador_pdf.py`, `exportador_html.py`, `exportador_excel.py`, `exportador_json.py`, `exportador_markdown.py`) para mantener responsabilidades separadas sin romper la CLI.
- `seo_auditor/services/informe_service.py`: composición semántica del informe como fuente única para Word/PDF/HTML con reglas condicionales por fuentes (GSC/GA4/IA).
- Contrato documental interno: `exportar_markdown_ia` genera `*_ia.md` solo para revisión editorial interna; DOCX/PDF/HTML deben renderizar siempre desde `construir_modelo_semantico_informe`.
- La plantilla HTML usa clases semánticas (`.cabecera`, `.meta`, `.kpi-card`, `.prioridad`, `.tabla-ejecutiva`) con tipografía escalada y tablas premium portables sin dependencias JavaScript.

## Notas de mantenimiento
- El flujo admite degradación elegante: si una fuente externa falla, el proceso general continúa.
- La salida separa capa ejecutiva y capa técnica para facilitar lectura por perfiles no técnicos y técnicos.
- La priorización de páginas dispone de una función explicable (`calcular_score_prioridad_pagina`) preparada para evolucionar a un motor SEO multi-componente.

- `seo_auditor/web/`: primera capa web interna con Django (dashboard, formulario, estado y descargas) conectada al núcleo de servicios.
