# version.md

## 0.3.0 - 2026-03-19
- Se rehace la maquetación de Word para formato corporativo real: portada con aire visual, tabla KPI, secciones editoriales y anexo técnico separado.
- Se mejora la exportación PDF para heredar estructura ejecutiva y evitar markdown crudo mediante transformación intermedia IA → secciones.
- Se añade parser de narrativa IA (`sections = [{titulo, tipo, items}]`) para render limpio en DOCX/PDF.
- Se corrige y refuerza el dashboard Excel con rejilla fija, gráficos no solapados y hoja auxiliar oculta `AuxDashboard` para cálculos/rangos.
- Se mejora legibilidad de hoja `Errores` con wrap text, alineación superior, anchos útiles y alturas de fila operativas.
- Se revisa el score SEO con fórmula ponderada menos punitiva y documentada en métricas.
- Se actualizan tests de reporters para transformación de secciones y score.

## 0.2.1 - 2026-03-19
- Se corrige un error en exportación PDF cuando el resumen IA incluye etiquetas HTML no compatibles con ReportLab (ej. `<link rel=...>`).
- Se añade saneamiento de texto para PDF y test de regresión asociado.

## 0.2.0 - 2026-03-19
- Se añade estructura de salida profesional por dominio y fecha real (`<output>/<slug>/<fecha>`).
- Se incorpora parámetro CLI `--gestor` con valor por defecto `Juan Antonio Sánchez Plaza`.
- Se incorpora parámetro CLI `--max-muestras-ia` para controlar coste de tokens.
- Se amplían modelos con metadatos de cliente, fecha y gestor.
- Se implementa clasificación automática robusta por severidad, área, impacto, esfuerzo y prioridad.
- Se mejora JSON y Markdown con metadatos de informe.
- Se rediseña Excel con hojas `Dashboard`, `Errores` y `Roadmap`, fórmulas dinámicas, gráficos y validaciones.
- Se mejora Word/PDF con estructura profesional (portada, KPIs, bloques ejecutivos y anexo técnico).
- Se optimiza la capa de contexto para IA con datos agregados y muestras limitadas.
- Se actualizan tests y documentación asociada.

## 0.1.0 - 2026-03-19
- Estructura inicial profesional del proyecto.
- CLI base para auditoría desde sitemap.
- Validación de URLs y sitemap.
- Recolección técnica de señales SEO esenciales.
- Exportación a JSON, Excel, Word y PDF.
- Integración opcional con Google AI Studio.
- Tests unitarios iniciales.
