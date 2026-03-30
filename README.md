# Auditor SEO Pro (Python)

Herramienta de auditoría SEO técnica y ejecutiva con exportación a JSON, Excel, Word, PDF, HTML y Markdown, con integraciones opcionales de IA (Gemini), PageSpeed Insights, Google Search Console y Google Analytics 4.

## Objetivo del proyecto
- Auditar URLs a partir de un sitemap XML.
- Detectar incidencias SEO técnicas y de contenido por URL.
- Medir rendimiento con PageSpeed (mobile/desktop).
- Enriquecer narrativa del informe con IA de forma opcional.
- Incorporar datos autenticados de GSC y GA4 cuando estén disponibles.
- Generar entregables ejecutivos y técnicos en múltiples formatos.

## Arquitectura de informes (capa semántica unificada)
- La generación documental usa una capa intermedia única (`construir_modelo_semantico_informe`) que transforma datos técnicos + narrativa IA en una estructura neutral de secciones y bloques.
- DOCX, PDF y HTML consumen esa misma capa semántica para mantener el mismo contenido base (tablas, párrafos, tarjetas y notas) con diferencias visuales razonables por formato.
- La capa de exportación está modularizada por formato dentro de `src/seo_auditor/documentacion/`: `modelo/`, `builders/`, `shared/` y `exportadores/` separan responsabilidades; `src/seo_auditor/reporters/` permanece como capa puente de compatibilidad.
- El Markdown IA se mantiene como exportación adicional (`*_ia.md`) para revisión editorial, pero ya no es la fuente directa de maquetación final.
- La sanitización editorial normaliza narrativa antes de renderizar:
  - limpieza de residuos markdown,
  - normalización de listas y saltos,
  - normalización de formatos numéricos comunes.
- Política de compatibilidad de emojis:
  - en PDF y DOCX se aplica texto seguro sin emoji para compatibilidad tipográfica estable,
  - en HTML se mantiene política homogénea de texto seguro (sin emoji) y queda preparado para iconografía CSS controlada,
  - en Excel se aplica texto corto seguro para legibilidad de celdas.
- Política de placeholders:
  - cualquier token residual tipo `[TOKEN_MAYUSCULA]` se normaliza a texto legible en la capa editorial,
  - además se ejecuta una sanitización final de exportación que bloquea corchetes residuales antes de generar DOCX/PDF/HTML.
- Periodo analizado:
  - se expone como metadato editorial principal en Word, PDF, HTML y Excel (cabeceras/portada),
  - deja de quedar oculto como una línea secundaria del resumen narrativo.
- Excel:
  - la hoja `Contenido` se construye ahora por URL consolidada para evitar duplicados por incidencia,
  - el detalle por incidencia sigue en la hoja `Errores`.

## Papel del archivo Markdown IA
- El archivo `*_ia.md` se mantiene como salida auxiliar interna para revisión editorial.
- Es un artefacto contractual de revisión interna y no es la fuente de layout final.
- No es el artefacto principal de cliente.
- La maquetación premium final (Word/PDF/HTML) se construye desde la capa semántica intermedia, no desde markdown directo.

## Priorización SEO de páginas (base preparada para evolución)
- La puntuación de páginas prioritarias se calcula ahora con una función explícita y trazable (`calcular_score_prioridad_pagina`).
- El resultado incluye:
  - `score_prioridad`,
  - `motivos` legibles,
  - `explicacion_prioridad` por componentes (`potencial_seo`, `oportunidad_ctr`, `oportunidad_conversion`, `friccion_tecnica_onpage`, `esfuerzo_estimado`).
- Esta estructura deja lista la evolución hacia un motor de priorización más robusto y explicable sin romper la CLI actual.

## Requisitos
- Python 3.11 o superior.
- Acceso a internet para rastreo web y APIs externas.

## Instalación y entorno

### Linux / macOS
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (CMD)
```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Variables de entorno (`.env`)
> Las claves y parámetros se configuran en `.env` o en variables del sistema. Nunca en el código.

### IA (Gemini)
- `GEMINI_API_KEY`
- `GEMINI_MODEL` (por defecto: `gemini-2.5-flash`)

### Núcleo de rastreo
- `HTTP_TIMEOUT` (por defecto: `15`)
- `MAX_URLS` (por defecto: `200`)

### PageSpeed
- `PAGESPEED_API_KEY`
- `MAX_PAGESPEED_URLS` (por defecto: `5`)
- `PAGESPEED_TIMEOUT` (por defecto: `45`)
- `PAGESPEED_REINTENTOS` (por defecto: `2`)

### Caché
- `CACHE_TTL_SEGUNDOS` (por defecto: `21600`)

### Google Search Console
- `GSC_ENABLED` (`true/false`)
- `GSC_SITE_URL`
- `GSC_CREDENTIALS_FILE`
- `GSC_DATE_FROM` / `GSC_DATE_TO` (el CLI puede sobrescribirlas)
- `GSC_ROW_LIMIT` (por defecto: `250`)

### Google Analytics 4
- `GA_ENABLED` (`true/false`)
- `GA_PROPERTY_ID`
- `GA_CREDENTIALS_FILE`
- `GA_DATE_FROM` / `GA_DATE_TO` (el CLI puede sobrescribirlas)
- `GA_ROW_LIMIT` (por defecto: `1000`)

## Ejecución rápida
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas
```

## Todos los CLI disponibles

### Auditoría SEO general
- `--sitemap <url>`: sitemap a auditar (obligatorio en modo auditoría estándar).
- `--output <ruta>`: carpeta raíz de salida (`./salidas` si no se indica).
- `--gestor "Nombre Apellidos"`: responsable del informe.
- `--cliente "Nombre cliente"`: nombre de cliente (usado en informe GA4 premium o inferencia cuando aplique).
- `--modo-rapido`: limita URLs para una auditoría más corta.

### IA
- `--usar-ia`: activa narrativa con IA.
- `--testia`: prueba de conectividad IA (sin auditoría completa).
- `--modelo-ia <modelo>`: sobrescribe el modelo para esta ejecución.
- `--max-muestras-ia <N>`: máximo de muestras agregadas para IA.
- `--modo <completo|resumen|quickwins|gsc|roadmap|entrega-completa|informe-ga4>`:
  - En auditoría con IA usa plantillas de prompt (`completo`, `resumen`, `quickwins`, `gsc`, `roadmap`).
  - `entrega-completa` activa orquestación compuesta (auditoría SEO + bloque premium opcional).
  - `informe-ga4` activa modo dedicado de informe GA4 premium.
- `--generar-todo`: atajo operativo equivalente a `--modo entrega-completa`.

### PageSpeed
- `--pagepsi <url>`: analiza una URL concreta con PageSpeed.
- `--pagepsi-list <archivo>`: lista de URLs (una por línea).
- `--max-pagepsi-urls <N>`: límite de URLs para PageSpeed.
- `--pagepsi-timeout <N>`: timeout por petición.
- `--pagepsi-reintentos <N>`: reintentos (`-1` usa configuración).

### Caché
- `--cache-ttl <segundos>`: TTL de caché en esta ejecución.
- `--invalidar-cache`: borra caché local antes de ejecutar.

### Datos autenticados
- `--noGSC`: desactiva GSC en esta ejecución.
- `--testgsc`: prueba conectividad GSC.
- `--testga`: prueba conectividad GA4.

### Ventana temporal
- `--date-from <YYYY-MM-DD>`
- `--date-to <YYYY-MM-DD>`

Reglas:
- Deben enviarse juntas.
- Formato ISO obligatorio.
- `date-from` debe ser anterior a `date-to`.
- Si no se informan, se usa por defecto una ventana de 28 días (de ayer hacia atrás, inclusive).

### Modo dedicado GA4 premium
- `--modo informe-ga4`
- `--comparar <periodo-anterior|anio-anterior>`
- `--provincia <nombre>`
- `--cliente <nombre>`

### Perfiles de generación compuesta
- `auditoria-seo-completa`: perfil por defecto de la CLI histórica (JSON, Excel, Word, PDF, HTML, Markdown IA).
- `todo`: perfil compuesto (equivalente a `--generar-todo` o `--modo entrega-completa`) que añade GA4 premium de forma controlada.
- `solo-ga4-premium`: perfil interno del modo `--modo informe-ga4`.

Comportamiento del orquestador:
- Ejecuta la auditoría base una sola vez.
- Reutiliza el resultado consolidado para todos los exportadores SEO.
- Intenta exportar cada entregable de forma aislada (degradación elegante).
- Informa en logs: perfil activo, fuentes, entregables planificados, generados, omitidos y errores no fatales.
- Si GA4 premium no está disponible (por configuración o error), se omite sin romper el resto de entregables.

## Ejemplos de generación compuesta
```bash
python src/main.py --sitemap https://www.colegiolegamar.com/sitemap_index.xml --output ./salidas --usar-ia --date-from 2026-02-01 --date-to 2026-02-28 --generar-todo
python src/main.py --sitemap https://www.colegiolegamar.com/sitemap_index.xml --output ./salidas --usar-ia --date-from 2026-02-01 --date-to 2026-02-28 --modo entrega-completa
python src/main.py --modo entrega-completa --sitemap https://www.colegiolegamar.com/sitemap_index.xml --comparar periodo-anterior --cliente 'Colegio Legamar'
```

## Archivo de referencia de CLI
Se incluye documentación ampliada y ejemplos completos en [`CLI.md`](./CLI.md).

## Estructura de salida
### Auditoría SEO completa
```text
<output>/<slug_dominio>/<YYYY-MM-DD>/
```

### Informe dedicado GA4 premium
```text
<output>/ga4_premium/<YYYY-MM-DD>/
```

## Tests
```bash
pytest -q
```

## Versionado
Consulta el historial de cambios en [`version.md`](./version.md).
