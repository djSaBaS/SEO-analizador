# version.md

## 0.8.2 - 2026-03-24
- Se alinea `PROMPT_IA_FALLBACK` con el contenido oficial de `Prompt/consulta_ia_prompt.txt` para evitar desvíos hacia un prompt simplificado.
- Se corrige `generar_resumen_ia` para construir el prompt mediante `construir_prompt_ia` (reemplazo explícito de `{datos_json}`) en lugar de `str.format` directo.
- Se actualiza documentación de `src/info.md` para reflejar el uso de plantilla externa editable con fallback equivalente.

## 0.8.1 - 2026-03-24
- Se corrige la clasificación de patrones no indexables para evaluar rutas por segmentos (evitando falsos positivos como `/formacion-*` por la regla `/form`).
- Se mejora el cruce con Search Console normalizando URLs de auditoría y GSC (incluyendo fallback por `url_final`) para aplicar de forma consistente las reglas de `sin impresiones` y `sin clics`.
- Se alinea la prioridad de gestión de indexación con el número de motivos únicos mostrados en informe.
- Se optimiza el bloque narrativo de `Gestión de indexación` agrupando filas por clasificación en una sola pasada.
- Se mejora mantenibilidad en Excel moviendo anchos de `Indexacion` a un diccionario configurable.
- Se amplían tests para cubrir falsos positivos de patrones, normalización GSC y consistencia de clasificación.

## 0.8.0 - 2026-03-24
- Se añade gestión de indexación inteligente con clasificación por URL en `INDEXABLE`, `REVISAR` y `NO_INDEXAR`, aplicando reglas por patrones de URL, contenido, señales SEO y datos de Search Console.
- Se incorpora el modelo de datos de decisiones de indexación (`url`, `clasificacion`, `motivo`, `accion_recomendada`, `prioridad`) dentro del resultado consolidado de la auditoría.
- Se amplían los reportes con nueva sección narrativa `Gestión de indexación` (resumen global, URLs no indexables, URLs a revisar y recomendaciones claras).
- Se añade hoja Excel `Indexacion` y KPIs de gestión de indexación en `Dashboard`.
- Se integra la nueva capa de indexación inteligente en `Quick wins`, `Roadmap` y exportación JSON.

## 0.7.0 - 2026-03-24
- Se integra Google Search Console como fuente autenticada opcional con degradación elegante: si falla por credenciales/permisos/propiedad, la auditoría no se rompe y se registra en `fuentes_fallidas`.
- Se añade argumento CLI `--noGSC` para omitir GSC en una ejecución concreta aunque esté configurado en entorno.
- Se amplían exportaciones JSON/Excel/Word/PDF/HTML con capa de visibilidad orgánica real, oportunidades SEO prioritarias y cruce técnico+GSC cuando la fuente está activa.
- Se añaden hojas Excel `Search_Console_Paginas`, `Search_Console_Queries` y `Oportunidades_GSC`, además de nuevos KPIs de clics, impresiones, CTR y posición media.
- Se evoluciona la priorización de quick wins y roadmap hacia enfoque de crecimiento SEO real por impacto y oportunidad.

## 0.6.1 - 2026-03-23
- Se corrige el análisis de robots para respetar el alcance por `User-agent` y evitar falsos positivos de bloqueo en sitemap.
- Se mejora la detección de bloqueo combinando parser estándar de robots (allow/disallow completo) con fallback por patrones.
- Se corrige exportación Excel moviendo la carga de la hoja `Contenido` dentro de `exportar_excel` (antes estaba en bloque inalcanzable).
- Se mejora HTML de incidencias: ordenado por severidad (alta→informativa) y coloreado pastel por nivel.
- Se añaden tests de regresión para filtrado de `Disallow` por user-agent y orden de severidad en HTML.

## 0.6.0 - 2026-03-23
- Se integra análisis de contenido real con trafilatura (palabras, densidad, ratio texto/HTML, calidad de contenido y thin content) con detección de duplicidad aproximada por hash.
- Se añade análisis de indexación y rastreo con advertools sobre robots.txt y coherencia sitemap vs robots, incluyendo sección dedicada en narrativa de informes.
- Se amplía el modelo de datos por URL con métricas de contenido, estructura de headings, lazy-load e imágenes sin ALT para reporting accionable.
- Se agrega hoja Excel `Contenido` y se extiende `Errores` con categoría para priorización operativa.
- Se mantiene compatibilidad CLI permitiendo ejecución sin `--output` mediante fallback automático a `./salidas`.

## 0.5.3 - 2026-03-23
- Se corrige Quick Wins para agrupar por URL (problemas y recomendaciones deduplicadas), calcular impacto máximo y esfuerzo mínimo, y limitar la salida ejecutiva a un conjunto útil.
- Se actualiza la visualización de Quick Wins en Word/PDF/HTML a formato tipo tarjeta en lugar de tabla plana.
- Se asegura fallback obligatorio de Roadmap en fase de medio plazo para evitar contenido vacío.
- Se añade gráfico de comparación entre incidencias técnicas e incidencias agrupadas en dashboard Excel.
- Se ajustan colores por severidad del Excel a esquema ejecutivo solicitado (rojo/naranja/amarillo/azul).

## 0.5.2 - 2026-03-23
- Se mejora la presentación de rendimiento en Word/PDF/HTML con formato compacto por métrica (vertical), evitando tablas excesivamente horizontales y manteniendo `No disponible` para datos ausentes.
- Se rehace la capa de quick wins para deduplicar por URL/acción, filtrar entradas incompletas y mostrar estructura consistente (URL, problema, recomendación, impacto, esfuerzo).
- Se añade capa de incidencias agrupadas ejecutivas para mantener coherencia entre resumen ejecutivo y detalle técnico de Excel/anexo.
- Se amplía el análisis on-page con detección de duplicados de `title` y `meta description` a nivel conjunto auditado, además de H1 vacío y conteo agregado de imágenes sin alt útil.
- Se incorpora desglose del score por bloques (`indexacion_arquitectura`, `contenido_onpage`, `rendimiento`, `multimedia_accesibilidad`) para mejorar interpretabilidad en JSON y dashboard.
- Se evoluciona el dashboard Excel con KPIs adicionales (agrupadas, score por bloques, métricas on-page clave) y gráfico de score por bloques.

## 0.5.1 - 2026-03-23
- Se corrige una regresión en canonical: las canonicals plenamente coherentes ya no se marcan como hallazgo de diferencia menor.
- Se robustece la normalización de URL para tolerar puertos inválidos en canonicals sin romper la auditoría completa de la URL.
- Se corrige `--invalidar-cache` para eliminar entradas JSON de forma recursiva en subcarpetas (`.cache/pagespeed` y `.cache/ia`).
- Se añaden tests de regresión para canonical coherente, tolerancia a puerto inválido e invalidación recursiva de caché.

## 0.5.0 - 2026-03-20
- Se corrige la lógica de canonical para reducir falsos positivos: comparación robusta con normalización de esquema, host, puertos por defecto, slash final, query y fragmentos.
- Se introducen niveles de canonical (`diferencia menor`, `potencialmente incoherente`, `realmente incoherente`) con severidad/prioridad más realistas.
- Se amplía el análisis on-page con validación de longitudes de `title` y `meta description`, detección de múltiples H1 e imágenes sin `alt`.
- Se profesionaliza la sección de rendimiento en Word/PDF con tabla comparativa mobile vs desktop, interpretación visual y listado estructurado de oportunidades.
- Se evoluciona el dashboard Excel con nuevas KPI cards (incidencias por severidad, URLs sanas, % con incidencias, % resueltas, oportunidades y medias de rendimiento).
- Se añade caché local reutilizable para IA y PageSpeed con TTL configurable e invalidación por CLI.
- Se añade `--modo-rapido` para auditorías ligeras y exportación adicional a HTML.

## 0.4.3 - 2026-03-20
- Se corrige el tratamiento de PageSpeed cuando falla por timeout/red: no se marca como fuente activa sin métricas válidas y se registra en `fuentes_fallidas` con `pagespeed_estado` estructurado.
- Se añaden timeout y reintentos configurables para PageSpeed (`PAGESPEED_TIMEOUT`, `PAGESPEED_REINTENTOS`, `--pagepsi-timeout`, `--pagepsi-reintentos`) con backoff simple y logs de intentos.
- Se evita renderizar métricas `None` en Word/PDF y se muestra mensaje profesional cuando PageSpeed no está disponible por timeout/error.
- Se corrige la robustez de Excel para evitar conflictos de tabla/autofiltro y se añaden validaciones automáticas de tabla de rendimiento.
- Se añaden tests para flujo PageSpeed fallido, mensaje narrativo de rendimiento no disponible y validez de tabla `TablaRendimiento`.

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
