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


## Estado de migración (fases)
- **Fase 1: cerrada (2026-03-31).**
  - Exportadores consolidados en `src/seo_auditor/documentacion/exportadores/`.
  - Wrappers de compatibilidad activos en `src/seo_auditor/reporters/`.
  - Artefactos de salida equivalentes conservados (nombres/rutas/formatos).
  - Validación documental en verde con tests específicos de `documentacion`/`reporters`.
- **Fase 2: cerrada (2026-03-31).**
  - Módulos funcionales divididos en `integrations`, `analyzers` y `services`.
  - CLI estable y mantenida sin ruptura de flags/flows públicos.
  - Tests reorganizados en `tests/unit` y `tests/integration` con compatibilidad de rutas legacy.
- **Fase 3: cerrada (2026-04-01).**
  - Contratos tipados estabilizados (`AuditoriaRequest`, `AuditoriaResult`) con pruebas dedicadas en `tests/unit`.
  - Equivalencia estructural validada entre ejecución CLI histórica y `AuditoriaService`.
  - Degradación elegante validada ante indisponibilidad de integraciones externas (GSC/GA4/PageSpeed/IA).
  - Validación de entregables por perfil (`auditoria-seo-completa`, `todo`, `solo-ga4-premium`) cubierta en pruebas.

### Criterios de cierre por fase
- **Fase 1 (documentación/exportación):** paridad de artefactos (DOCX/PDF/HTML/Excel/JSON) + wrappers legacy activos + tests documentales verdes.
- **Fase 2 (modularización funcional):** CLI sin ruptura de flags/modos + módulos separados (`integrations`, `analyzers`, `services`) + tests unit/integration reorganizados.
- **Fase 3 (contratos/orquestación):** contratos `AuditoriaRequest/AuditoriaResult` estables + equivalencia CLI↔servicio + degradación elegante e invariantes de perfiles verificadas.

### Changelog de migración
Se mantiene en `docs/arquitectura/changelog_migracion.md` con tres bloques fijos por iteración:
- `módulos movidos`,
- `compatibilidades mantenidas`,
- `riesgos pendientes`.

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

## Ejemplo: informe completo del último mes

> Referencia temporal: hoy es **2026-04-01**. El último mes completo es **2026-03-01 a 2026-03-31**.

```bash
python src/main.py \
  --sitemap https://www.ejemplo.com/sitemap.xml \
  --output ./salidas \
  --usar-ia \
  --modo entrega-completa \
  --date-from 2026-03-01 \
  --date-to 2026-03-31
```

Si prefieres calcular fechas automáticamente en Linux/macOS:

```bash
FROM=$(date -u -d "$(date -u +%Y-%m-01) -1 month" +%F)
TO=$(date -u -d "$(date -u +%Y-%m-01) -1 day" +%F)
python src/main.py --sitemap https://www.ejemplo.com/sitemap.xml --output ./salidas --usar-ia --modo entrega-completa --date-from "$FROM" --date-to "$TO"
```

Para ejecución programática con `AuditoriaService`, revisa `docs/ejemplos/ejecucion_servicios.md`.

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

## Norma documental de carpetas (`info.md`)
- Cada carpeta nueva debe crearse junto con su archivo `info.md` en el mismo commit.
- El `info.md` debe usar la plantilla mínima: objetivo, archivos, responsabilidades, dependencias internas, flujo de uso, notas de mantenimiento y mejoras futuras.
- La regla aplica a carpetas legacy y canónicas (por ejemplo, `Prompt/` y `prompts/`), subcarpetas en `src/seo_auditor/` y futuras carpetas como `tests/fixtures/`.
- Validación automática:

```bash
python scripts/mantenimiento/validar_entorno.py
```

Más detalle en [`docs/arquitectura/sistema_documental.md`](./docs/arquitectura/sistema_documental.md).

## Tests
```bash
pytest -q
```

## Versionado
Consulta el historial de cambios en [`version.md`](./version.md).


## Capa web interna (Django)
Esta fase incorpora una primera interfaz web **interna/local** que reutiliza los servicios ya consolidados (`AuditoriaService`, `EntregablesService`, contratos `AuditoriaRequest/AuditoriaResult`) sin duplicar lógica de negocio.

### Qué incluye en esta fase
- Dashboard interno con ejecuciones recientes y documentos detectados en `./salidas`.
- Formulario web para lanzar auditorías con parámetros clave (sitemap, cliente, gestor, periodo, IA, modo, PageSpeed, perfil de entregables).
- Vista de estado/resultado con resumen operativo, fuentes activas/fallidas, KPIs básicos y bloques de páginas prioritarias/quick wins.
- Descarga de entregables generados cuando el archivo existe en disco.
- Persistencia mínima en Django (`EjecucionAuditoria`) para registrar metadatos de ejecución sin sobredimensionar la plataforma.
- La vista web de detalle consume ahora prioridades reales del motor (`páginas prioritarias` y `quick wins`) usando la misma lógica de construcción que los exportadores.
- Se valida coherencia de dominio entre sitemap auditado y fuentes (GSC/GA4/PageSpeed URL manual): las fuentes incompatibles se excluyen y quedan trazadas en ejecución.

### Guía completa de puesta en marcha web (desde cero)

#### 1) Requisitos previos
- Python **3.11 o superior**.
- Estar situado en la **raíz del repositorio** (carpeta que contiene `README.md`, `requirements.txt` y `src/`).
- Tener `.env` preparado si quieres activar integraciones (GSC/GA4/PageSpeed/IA).

Comando para comprobar versión de Python:
```bash
python --version
```

#### 2) Crear y activar entorno virtual

##### Windows CMD
```bat
cd C:\ruta\a\SEO-analizador
python -m venv .venv
.venv\Scripts\activate.bat
```

##### Windows PowerShell
```powershell
cd C:\ruta\a\SEO-analizador
python -m venv .venv
.venv\Scripts\Activate.ps1
```

##### Linux / macOS
```bash
cd /ruta/a/SEO-analizador
python -m venv .venv
source .venv/bin/activate
```

#### 3) Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4) Configurar variables de entorno Django

Variables recomendadas en desarrollo local:
- `DJANGO_DEBUG=true`
- `DJANGO_SECRET_KEY=<valor_largo_aleatorio>`

Generar una clave segura desde Python:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Ejemplo en Linux/macOS:
```bash
export DJANGO_DEBUG=true
export DJANGO_SECRET_KEY="pega_aqui_la_clave_generada"
```

Ejemplo en Windows CMD:
```bat
set DJANGO_DEBUG=true
set DJANGO_SECRET_KEY=pega_aqui_la_clave_generada
```

Ejemplo en Windows PowerShell:
```powershell
$env:DJANGO_DEBUG = "true"
$env:DJANGO_SECRET_KEY = "pega_aqui_la_clave_generada"
```

> El proyecto carga `.env` mediante `python-dotenv`, así que también puedes guardar estas variables en un archivo `.env` en la raíz.

#### 5) Aplicar migraciones
Desde la **raíz del repositorio**:
```bash
python src/seo_auditor/web/manage.py migrate
```

#### 6) Arrancar servidor de desarrollo
Desde la **raíz del repositorio**:
```bash
python src/seo_auditor/web/manage.py runserver
```

URL esperada:
- `http://127.0.0.1:8000/`

> Alternativa si estás dentro de `src/seo_auditor/web/`: `python manage.py runserver`.

### Solución de problemas comunes (web)

#### Error: `ModuleNotFoundError: No module named 'seo_auditor'`
- Causa habitual: ejecutar fuera de la raíz o sin bootstrap correcto.
- Solución recomendada:
  1. Sitúate en la raíz del repositorio.
  2. Activa el entorno virtual.
  3. Ejecuta `python src/seo_auditor/web/manage.py runserver`.

#### Error por `DJANGO_SECRET_KEY` no definida
- Si `DJANGO_DEBUG=false`, la clave es obligatoria.
- Define `DJANGO_SECRET_KEY` en entorno o `.env` y vuelve a ejecutar.

#### Entorno virtual no activo
- Verifica que el prompt muestre `(.venv)`.
- Repite el comando de activación según tu sistema (CMD/PowerShell/Linux).

#### Dependencias no encontradas
- Ejecuta nuevamente `pip install -r requirements.txt` dentro del entorno virtual activo.

#### Descarga rechazada de un entregable
- La descarga de entregables solo permite archivos dentro de `./salidas` por seguridad.
- Si el archivo fue movido fuera de esa carpeta, vuelve a generar la auditoría o restaura la estructura de salida.

### Limitaciones actuales de esta fase
- Ejecución en segundo plano con `ThreadPoolExecutor` local y refresco básico en pantalla de detalle (sin cola distribuida ni workers externos).
- Interfaz orientada a uso interno técnico.
- Persistencia ligera centrada en trazabilidad de ejecuciones, no en multiusuario avanzado.
