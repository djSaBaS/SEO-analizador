# Arquitectura general (fase de transición)

## Estado actual y objetivo

Este documento fija la **línea base de transición arquitectónica** para desacoplar la orquestación CLI, el núcleo de auditoría, conectores externos y reporting sin romper contratos existentes.

- Estado actual: arquitectura modular funcional con compatibilidad histórica en imports y CLI.
- Estado objetivo: módulos por dominio/capa con fachadas de compatibilidad temporal.
- Alcance de esta fase: **documentación + criterios de no ruptura + mapa de migración**.

---

## 1) Inventario de entrypoints actuales

### 1.1 `src/main.py` (entrypoint ejecutable)

- Función: punto de entrada mínimo del ejecutable Python.
- Comportamiento: delega en `seo_auditor.cli.main()` y devuelve su exit code.
- Contrato: no añade flags ni lógica propia; mantiene el bootstrap estable.

### 1.2 `src/seo_auditor/cli.py` (entrypoint real de orquestación)

#### Flags/modos principales

> Referencia de tipos y formato para evitar ambigüedad durante la transición.

| Flag | Tipo esperado | Formato / restricciones | Notas operativas |
|---|---|---|---|
| `--sitemap` | `str` | URL HTTP/HTTPS válida | Obligatorio en auditoría normal (excepto `--testia`, `--testga`, `--testgsc`). |
| `--output` | `str` | Ruta de directorio | Si falta, fallback a `./salidas`. |
| `--usar-ia` | `bool` (flag) | sin valor (`store_true`) | Activa enriquecimiento narrativo con IA. |
| `--modelo-ia` | `str` | Nombre de modelo | Vacío => usa configuración (`gemini_model`). |
| `--max-muestras-ia` | `int` | entero positivo (`>0`) | Controla volumen de muestras para IA. |
| `--testia` | `bool` (flag) | sin valor (`store_true`) | Prueba conectividad IA y finaliza. |
| `--testga` | `bool` (flag) | sin valor (`store_true`) | Prueba conectividad GA4 y finaliza. |
| `--testgsc` | `bool` (flag) | sin valor (`store_true`) | Prueba conectividad GSC y finaliza. |
| `--modo` | `str` (enum) | `completo`/`resumen`/`quickwins`/`gsc`/`roadmap`/`informe-ga4`/`entrega-completa` | Selector de ejecución principal. |
| `--generar-todo` | `bool` (flag) | sin valor (`store_true`) | Atajo equivalente a `--modo entrega-completa`. |
| `--pagepsi` | `str` | URL HTTP/HTTPS válida | Mutuamente excluyente con `--pagepsi-list`. |
| `--pagepsi-list` | `str` | Ruta a archivo de texto (1 URL por línea) | Si no hay URLs válidas, fallback a HOME. |
| `--max-pagepsi-urls` | `int` | entero `>= 0` | `0` => usa configuración. |
| `--pagepsi-timeout` | `int` | entero `>= 0` (segundos) | `0` => usa configuración. |
| `--pagepsi-reintentos` | `int` | entero (negativo => configuración) | Define reintentos por URL/estrategia. |
| `--noGSC` | `bool` (flag) | sin valor (`store_true`) | Desactiva GSC solo para esa ejecución. |
| `--invalidar-cache` | `bool` (flag) | sin valor (`store_true`) | Limpia caché local antes de ejecutar. |
| `--cache-ttl` | `int` | entero `>= 0` (segundos) | `0` => usa configuración. |
| `--modo-rapido` | `bool` (flag) | sin valor (`store_true`) | Reduce alcance para ejecución rápida. |
| `--cliente` | `str` | texto libre | Opcional, usado en portada GA4 premium. |
| `--gestor` | `str` | texto libre | Responsable mostrado en metadatos. |
| `--comparar` | `str` (enum) | `periodo-anterior` / `anio-anterior` | Solo aplica a informe GA4 premium. |
| `--provincia` | `str` | texto libre | Filtro opcional de detalle local GA4 premium. |
| `--date-from` | `str` | `YYYY-MM-DD` | Debe enviarse junto con `--date-to`. |
| `--date-to` | `str` | `YYYY-MM-DD` | Debe enviarse junto con `--date-from`; `date_from < date_to`. |

#### Resolución de perfil de generación

- `--generar-todo` => perfil `todo`.
- `--modo informe-ga4` => perfil `solo-ga4-premium`.
- `--modo entrega-completa` => perfil `todo`.
- resto => perfil `auditoria-seo-completa`.

#### Rutas de salida y nombres de artefactos (contrato vigente)

- **Auditoría SEO estándar**:
  - Ruta base: `<output>/<slug_dominio>/<fecha_iso>/`.
  - Fallback de output: `./salidas`.
  - Artefactos SEO con prefijo histórico (`construir_prefijo_archivo(resultado)`):
    - `<prefijo>_tecnico.json`
    - `<prefijo>.xlsx`
    - `<prefijo>.docx`
    - `<prefijo>.pdf`
    - `<prefijo>.html`
    - `<prefijo>_ia.md` (interno editorial)
- **GA4 premium (modo dedicado o perfil compuesto)**:
  - Ruta: `<output>/ga4_premium/<fecha_iso>/`.
  - Archivos:
    - `informe_ga4_premium.html`
    - `informe_ga4_premium.pdf`
    - `informe_ga4_premium.xlsx`

---

## 2) Matriz “módulo actual → módulo destino”

> Objetivo: preparar estructura por capas sin ruptura inmediata. Los módulos destino son la referencia de transición para siguientes PRs.

| Módulo actual | Módulo destino (transición) | Nota de migración |
|---|---|---|
| `seo_auditor/fetcher.py` | `seo_auditor/core/acquisition/sitemap_fetcher.py` | Extracción/normalización de URLs desde sitemap. |
| `seo_auditor/analyzer.py` | `seo_auditor/core/audit/technical_auditor.py` | Núcleo de auditoría técnica y consolidación principal. |
| `seo_auditor/pagespeed.py` | `seo_auditor/connectors/pagespeed/client.py` | Cliente PageSpeed + mapeo de métricas de rendimiento. |
| `seo_auditor/gsc.py` | `seo_auditor/connectors/gsc/client.py` | Integración GSC (paginas/queries/oportunidades). |
| `seo_auditor/ga4.py` | `seo_auditor/connectors/ga4/client.py` | Integración GA4 estándar para capa analítica base. |
| `seo_auditor/ga4_premium.py` | `seo_auditor/use_cases/ga4_premium/report_builder.py` | Caso de uso dedicado para informe premium GA4. |
| `seo_auditor/cache.py` | `seo_auditor/platform/cache/local_cache.py` | Infraestructura de caché local + TTL/invalidación. |
| `seo_auditor/utils.py` | `seo_auditor/shared/utils/{urls.py,dates.py,io.py,text.py}` | Fragmentación por responsabilidad (sin mega-módulo). |
| `seo_auditor/reporters/*` | `seo_auditor/presentation/reporting/*` | Capa de presentación/documentos y exportadores. |

---

## 3) Imports públicos a mantener temporalmente (fachadas/wrappers)

Durante la transición, **deben seguir funcionando** estos imports externos para no romper CLI/tests/consumidores:

- `from seo_auditor.fetcher import extraer_urls_sitemap`
- `from seo_auditor.analyzer import auditar_urls`
- `from seo_auditor.pagespeed import analizar_pagespeed_url, detectar_home`
- `from seo_auditor.gsc import cargar_datos_search_console`
- `from seo_auditor.ga4 import cargar_datos_analytics`
- `from seo_auditor.ga4_premium import generar_informe_ga4_premium`
- `from seo_auditor.cache import invalidar_cache`
- `from seo_auditor.utils import ...` (helpers actualmente consumidos por CLI/tests)
- `from seo_auditor.reporters import exportar_json, exportar_excel, exportar_word, exportar_pdf, exportar_html, exportar_markdown_ia`

### Estrategia de compatibilidad temporal

- Opción A (preferente): mantener módulo histórico como wrapper delegando al destino nuevo.
- Opción B: mover implementación y dejar fachada en `legacy/` reexportada desde módulo histórico.
- Regla: toda deprecación debe ser gradual, explícita y con ventana mínima de 1 ciclo de versión.

---

## 4) Criterio de “no ruptura” (Definition of Done de transición)

Se considera transición válida solo si se cumple **todo**:

1. **Interfaz CLI idéntica**:
   - mismos flags,
   - mismas opciones de `--modo`,
   - mismo comportamiento de `--generar-todo` y `--test*`.
2. **Artefactos de salida idénticos**:
   - mismos nombres de archivo,
   - misma estructura de carpetas,
   - mismo fallback de `--output` a `./salidas`.
3. **Compatibilidad de rutas de tests**:
   - imports legacy vigentes,
   - paths esperados por tests sin cambios,
   - sin renombrar fixtures/rutas públicas sin capa de compatibilidad.
4. **Degradación elegante preservada**:
   - fallo de integración externa no bloquea ejecución global cuando así está definido hoy.

Checklist operativo mínimo por PR de transición:

- [ ] `crear_parser()` mantiene contrato de argumentos.
- [ ] `main()` conserva rutas y códigos de salida por modo.
- [ ] Exportadores mantienen nombres de artefactos.
- [ ] Wrappers de compatibilidad activos para imports públicos.
- [ ] Tests de CLI/regresión de rutas siguen en verde.

---

## 5) Estado de fase

A partir de este documento, se declara formalmente:

> **Fase de transición iniciada**.

Este estado implica que las siguientes iteraciones priorizarán migración interna por capas manteniendo contrato público estable.
