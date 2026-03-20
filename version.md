# version.md

## 0.4.2 - 2026-03-20
- Se corrige el flujo funcional de PageSpeed extremo a extremo con trazabilidad de errores por URL/estrategia y fallback a HOME cuando `--pagepsi-list` no aporta URLs válidas.
- Se añaden barras de progreso en consola para auditoría técnica, ejecución de PageSpeed y exportación de entregables.
- Se restaura y mejora la capa visual de Excel: colores por severidad en `Errores`, legibilidad (anchos/altos/wrap/alineación), filtros, paneles congelados y recuperación de gráficos en `Dashboard` con hoja auxiliar oculta.
- Se añaden tests de regresión para flujo CLI de persistencia de `rendimiento` y `fuentes_activas`, existencia de gráficos en Excel y conservación de color por severidad.
- Se actualiza `.env.example` y README para dejar explícito que las API keys deben configurarse en `.env`/entorno y no en `config.py`.

## 0.4.1 - 2026-03-20
- Se atienden comentarios de revisión eliminando una comprobación redundante en CLI al resolver URLs de PageSpeed.
- Se refactorizan `construir_filas` y `construir_filas_rendimiento` para reducir duplicación mediante filas base reutilizables.
- Se corrige el KPI de score medio móvil/escritorio en Excel para calcularse desde ejecuciones únicas de PageSpeed y no desde filas expandidas por oportunidad.
- Se refuerza el fallback de narrativa ejecutiva para rellenar todas las secciones obligatorias cuando la IA no esté activa o no devuelva contenido usable.
- Se añaden pruebas de regresión para fallback completo de bloques narrativos y para validación del cálculo de score medio en Dashboard.

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
