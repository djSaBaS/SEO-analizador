## 0.10.4 - 2026-03-29
- Se mejora la calidad documental transversal de entregables SEO: se refuerza la cabecera editorial y metadatos en Word/PDF/HTML/Excel con presencia explícita del periodo analizado.
- Se actualiza la política de emojis para usar texto seguro corporativo (sin placeholders entre corchetes) y se añade limpieza de tokens residuales tipo `[TOKEN_MAYUSCULA]`.
- Se mejora el render de tablas PDF con wrapping real de celdas, anchos controlados y padding/valign para reducir desbordes y mejorar legibilidad.
- Se rediseña la cabecera HTML con formato más premium (portada, bloque de metadatos y tarjetas KPI mejor jerarquizadas), manteniendo salida portable.
- Se corrige la hoja `Contenido` de Excel para consolidar por URL y evitar duplicados por incidencia; el detalle por hallazgo se mantiene en `Errores`.
- Se amplían tests de reporters/HTML para cubrir nueva política editorial (emojis/placeholders), periodo visible y consolidación de contenido por URL.

## 0.10.3 - 2026-03-29
- Se ajusta la documentación de ejemplos CLI para usar comillas simples en `--cliente` y mejorar portabilidad de shell.
- Se elimina el perfil no utilizado `entrega-cliente` del mapa central de perfiles de generación en CLI para simplificar mantenimiento.

## 0.10.2 - 2026-03-26
- Se añade orquestación de generación compuesta en CLI con perfil centralizado de entregables y atajo `--generar-todo` (equivalente a `--modo entrega-completa`) sin romper compatibilidad de modos existentes.
- Se centraliza la definición de perfiles/entregables en `cli.py` para evitar condicionales dispersos y dejar base extensible (`auditoria-seo-completa`, `todo`, `solo-ga4-premium`).
- Se incorpora ejecución aislada de exportadores con degradación elegante: un fallo puntual de exportación no detiene el resto y queda trazado en resumen final.
- Se integra GA4 premium como entregable opcional dentro del perfil compuesto `todo`, con omisión controlada cuando GA4 no está habilitado o no hay datos.
- Se amplían tests de CLI para perfiles de generación, compatibilidad del nuevo modo, degradación por fallo de exportador e invocación de GA4 premium en `--generar-todo`.
- Se actualiza documentación operativa (`README.md`, `CLI.md`, `src/info.md`, `tests/info.md`, `docs/info.md`) para reflejar el nuevo flujo compuesto.

## 0.10.1 - 2026-03-26
- Se corrige una regresión funcional en la capa semántica: la sección `Rendimiento y experiencia de usuario` vuelve a incluir tabla detallada de métricas PageSpeed y tabla de oportunidades priorizadas en DOCX/PDF/HTML.
- Se corrige el `colspan` de tablas vacías en HTML para que sea dinámico según el número real de columnas de cada tabla.
- Se amplían tests de regresión para validar el detalle de rendimiento en el modelo semántico y el `colspan` dinámico en exportación HTML.

## 0.10.0 - 2026-03-26
- Se implementa una capa semántica intermedia única del informe (`construir_modelo_semantico_informe`) para alinear DOCX, PDF y HTML desde una misma estructura de bloques.
- Se desacopla la maquetación final del markdown IA: el markdown se conserva como exportación adicional, pero la generación documental principal usa el modelo semántico neutral.
- Se incorpora sanitización editorial común (limpieza de markdown residual, normalización de saltos/formatos y compatibilidad de contenido narrativo).
- Se aplica política de compatibilidad de emojis para documentos, sustituyendo glifos conflictivos por etiquetas seguras y evitando cuadrados negros en PDF/DOCX.
- Se homogeneiza el uso de tablas en secciones clave (`KPIs`, `Comportamiento y conversión`, `Gestión de indexación`, `Páginas prioritarias`) para mejorar alineación visual y estructural entre formatos.
- Se extrae y documenta la lógica de priorización de páginas en `calcular_score_prioridad_pagina`, añadiendo explicación estructurada por componentes para preparar la siguiente fase del motor de priorización SEO.
- Se amplían tests de reporters para cubrir la capa semántica, la política de emojis y la trazabilidad del score de prioridad.

## 0.9.3 - 2026-03-26
- Se corrige la documentación de modelos Gemini para usar `gemini-2.5-flash` en ejemplos CLI y en la referencia de `GEMINI_MODEL` del README.
- Se alinea el valor por defecto de `GEMINI_MODEL` en configuración a `gemini-2.5-flash` para mantener consistencia entre código y documentación.
- Se actualizan tests que instanciaban configuración con `gemini-2.0-flash` para reflejar el modelo estándar actual del proyecto.

## 0.9.2 - 2026-03-26
- Se revisa y consolida la documentación general del proyecto para eliminar duplicidades e incoherencias entre archivos Markdown.
- Se actualiza `README.md` con inventario completo de parámetros CLI y configuración de entorno vigente.
- Se crea `CLI.md` con ejemplos de uso exhaustivos para todos los modos y banderas del CLI (auditoría, IA, PageSpeed, GSC, GA4 y caché).
- Se armonizan `docs/info.md`, `docs/arquitectura.md`, `docs/modo-pro-preparacion.md`, `src/info.md` y `tests/info.md` con el comportamiento real actual del sistema.

## 0.9.1 - 2026-03-26
- Se refuerza el modo `informe-ga4` con resolución robusta de cliente: prioridad a `--cliente`, inferencia desde sitemap HTTP y fallback desde ruta local (nombre de archivo).
- Se corrige la comparación `anio-anterior` para manejar años bisiestos (29 de febrero -> 28 de febrero del año previo).
- Se mejora mantenibilidad de `ga4_premium.py` extrayendo funciones auxiliares de carga, cálculo y exportación (HTML/Excel/PDF).
- Se eliminan números mágicos en insights y límites de Excel mediante constantes descriptivas.
- Se mejora el comparativo de adquisición usando merge `outer` para incluir canales presentes solo en el periodo comparado.
- Se añade aviso explícito cuando falla la generación de un gráfico PNG para PDF en lugar de silenciar el error.
- Se incorporan tests de regresión para comparación bisiesta e insights en `tests/test_ga4_premium.py`.

## 0.9.0 - 2026-03-26
- Se incorpora un nuevo modo CLI `--modo informe-ga4` para generar un informe GA4 premium dedicado sin ejecutar la auditoría SEO completa.
- Se añade exportación específica del informe GA4 premium a HTML interactivo (Plotly), PDF estático y Excel (`Dashboard` + hoja `GA4`) con comparación temporal (`--comparar`) y filtro provincial (`--provincia`).
- Se implementan nuevas consultas GA4 por secciones de negocio (KPIs, audiencia país/comunidad/ciudad, dispositivos, navegadores, adquisición, referidos, redes sociales y landing pages) más insights automáticos sobre páginas sin conversión, alto rebote y alto valor.
- Se mantiene degradación elegante: si GA4 no está disponible o falla la consulta, el modo dedicado no rompe la ejecución global.
- Se añaden dependencias `plotly` y `kaleido`, y test de regresión para validar el flujo CLI del modo `informe-ga4`.

## 0.8.6 - 2026-03-26
- Se corrige un bug crítico en `exportar_word` eliminando un bloque duplicado que usaba objetos de ReportLab dentro del flujo DOCX.
- Se mejora la mantenibilidad de `construir_paginas_prioritarias` sustituyendo números mágicos por constantes descriptivas de umbrales y puntuación.
- Se optimiza el bloque de `Comportamiento y conversión` evitando recálculos repetitivos al limitar páginas con tráfico sin conversión mediante contador incremental.
- Se añade test de regresión para asegurar que la exportación Word funciona con Analytics activo en la sección de comportamiento y conversión.

## 0.8.5 - 2026-03-26
- Se rediseña la exportación Excel con separación explícita entre `KPIs` (primera pestaña ejecutiva), `Dashboard` analítico y hojas de detalle, incorporando los KPI críticos de negocio (GSC, GA4 e indexación) sin necesidad de scroll horizontal.
- Se refuerza el dashboard con bloques visuales adicionales (comportamiento Analytics, top páginas/queries y páginas prioritarias), manteniendo compatibilidad cuando GSC o GA4 no están activos.
- Se aplica autoajuste global y legibilidad transversal (wrap/alturas/anchos) a todas las hojas relevantes del Excel, incluyendo KPIs, Analytics y auxiliares.
- Se amplía la narrativa y render de Word/PDF/HTML con la sección `Comportamiento y conversión`, la nueva sección `Páginas prioritarias` y un cruce GSC+GA4 más orientado a negocio.
- Se mejora el HTML para que deje de ser simplificado e incluya tablas de GA4, gestión de indexación, cruce inteligente y top oportunidades.
- Se actualizan pruebas de reporters para validar nueva jerarquía editorial y estructura de pestañas KPI/Dashboard.

## 0.8.4 - 2026-03-25
- Se implementa sistema de prompts modulares IA en `prompts/` con selector CLI `--modo` (`completo`, `resumen`, `quickwins`, `gsc`, `roadmap`).
- Se añade resolución de prompt por modo con fallback automático a `informe_general.txt` y compatibilidad retroactiva con la carpeta legacy `Prompt/`.
- Se amplía la inyección de contexto previo al prompt con JSON de control (`gsc_activo`, `analytics_activo`, `pagespeed_activo`, `fuentes_activas`, `modo`) sin romper el flujo IA existente.
- Se actualizan tests de `gemini_client` y flujo CLI para cubrir el nuevo modo de prompt y el contexto extendido.
- Se actualiza README con el listado completo de uso de `--modo` y ejemplos de ejecución por modo.

## 0.8.3 - 2026-03-25
- Se refuerza la consistencia Prompt→IA añadiendo `contexto_control` al JSON inyectado y endureciendo la validación post-IA para evitar contradicciones cuando `search_console` esté activa.
- Se amplían pruebas de regresión de `gemini_client` para cubrir coherencia por `fuentes_activas` y comportamiento correcto cuando GSC no está activo.
- Se rediseña el Dashboard de Excel con bloques ejecutivos más visuales (visibilidad orgánica real, score por bloques, oportunidades, gestión de indexación e incidencias), manteniendo gráficos sin solapes.
- Se aplica autoajuste global también al dashboard, con congelación de paneles para mejorar navegación y legibilidad completa en todas las hojas.
- Se mejora la escaneabilidad del HTML ejecutivo sustituyendo bloques lineales por listas compactas en secciones clave de GSC.
- Se corrige el helper `_renderizar_bloque_dashboard` para que devuelva la última fila realmente pintada también cuando el bloque no tenga líneas de detalle.

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
