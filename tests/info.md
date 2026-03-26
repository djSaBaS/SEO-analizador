# tests/info.md

Contiene pruebas unitarias y de regresión.

## Objetivo
- Validar utilidades críticas de URLs y slug de dominio.
- Verificar clasificación automática de incidencias.
- Comprobar estructura tabular de seguimiento para reporting.
- Validar sanitización de texto para exportación PDF segura.
- Validar transformación IA→secciones sin markdown crudo.
- Validar detección de home para comportamiento por defecto de PageSpeed.
- Validar persistencia de rendimiento y fuentes activas en el flujo CLI.
- Verificar existencia de gráficos y formato visual de severidad en el Excel final.
- Verificar consistencia del texto IA con fuentes activas (evitando negaciones de GSC cuando hay datos).
- Validar resolución de prompts modulares por modo (`--modo`) con fallback a `informe_general` y conservación de inyección `{datos_json}`.
- Validar mejoras de legibilidad del dashboard (bloques ejecutivos y panel congelado).
- Validar la nueva separación Excel `KPIs` + `Dashboard` y jerarquía editorial actualizada para Analytics.
- Validar regresión de exportación Word en la sección `Comportamiento y conversión` con Analytics activo.

- `test_indexacion.py`: valida filtrado de directivas Disallow por User-agent para evitar falsos positivos en robots.
- `test_indexacion.py`: valida filtrado de directivas Disallow por User-agent y clasificación inteligente de indexación (INDEXABLE/REVISAR/NO_INDEXAR) con señales de URL/contenido/SEO/GSC.
- `test_html_export.py`: valida orden por severidad en exportación HTML (alta arriba, informativa abajo).
