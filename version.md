# version.md

## 0.4.0 - 2026-03-20
- Se integra PageSpeed Insights con API pública, estrategias móvil/escritorio, extracción de scores Lighthouse, métricas clave (LCP/CLS/INP/FCP/TBT/Speed Index) y oportunidades accionables.
- Se añade comportamiento controlado de PageSpeed: por defecto analiza solo HOME, soporte `--pagepsi`, soporte `--pagepsi-list`, límite máximo y tolerancia a errores por URL.
- Se añade capa de métricas de campo públicas (CrUX vía `loadingExperience` cuando exista) separada de laboratorio.
- Se añade `--testia` y `--modelo-ia` para validación mínima de API/modelo sin generar entregables.
- Se mejora el contexto de IA para reducir tokens y reforzar la restricción de fuentes activas.
- Se amplían modelos de dominio con `fuentes_activas` y resultados de rendimiento tipados.
- Se corrige la generación documental para usar jerarquía editorial fija sin duplicidades narrativas y con anexo técnico estructurado al final.
- Se añade hoja `Rendimiento` al Excel con esquema de seguimiento operativo y KPIs de PageSpeed en Dashboard.
- Se actualiza documentación de arquitectura y preparación de modo pro.
- Se añaden pruebas para limpieza de markdown y detección de HOME en PageSpeed.

## 0.3.0 - 2026-03-19
- Se rehace la maquetación de Word para formato corporativo real: portada con aire visual, tabla KPI, secciones editoriales y anexo técnico separado.
- Se mejora la exportación PDF para heredar estructura ejecutiva y evitar markdown crudo mediante transformación intermedia IA → secciones.
- Se añade parser de narrativa IA (`sections = [{titulo, tipo, items}]`) para render limpio en DOCX/PDF.
- Se corrige y refuerza el dashboard Excel con rejilla fija, gráficos no solapados y hoja auxiliar oculta `AuxDashboard` para cálculos/rangos.
- Se mejora legibilidad de hoja `Errores` con wrap text, alineación superior, anchos útiles y alturas de fila operativas.
- Se revisa el score SEO con fórmula ponderada menos punitiva y documentada en métricas.
- Se actualizan tests de reporters para transformación de secciones y score.
