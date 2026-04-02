# Importa serialización JSON para enviar contexto técnico a la IA.
import json

# Importa contador para resumir hallazgos por frecuencia.
from collections import Counter

# Importa Path para caché local opcional y lectura de plantilla de prompt.
from pathlib import Path

# Importa utilidades de caché local reutilizable.
from seo_auditor.cache import construir_clave_cache, escribir_cache, leer_cache

# Importa el modelo de resultado global para tipado claro.
from seo_auditor.models import ResultadoAuditoria

# Define la carpeta principal del nuevo sistema modular de prompts.
RUTA_CARPETA_PROMPTS = Path(__file__).resolve().parents[2] / "prompts"

# Define carpeta heredada para compatibilidad retroactiva.
RUTA_CARPETA_PROMPTS_LEGACY = Path(__file__).resolve().parents[2] / "Prompt"

# Define la ruta heredada original del prompt único editable.
RUTA_PROMPT_UNICO_LEGACY = RUTA_CARPETA_PROMPTS_LEGACY / "consulta_ia_prompt.txt"

# Define el mapa de modos CLI a nombre de archivo de prompt.
MAPA_PROMPTS_POR_MODO = {
    "completo": "informe_general.txt",
    "resumen": "resumen_ejecutivo.txt",
    "quickwins": "quick_wins.txt",
    "gsc": "gsc_oportunidades.txt",
    "roadmap": "roadmap.txt",
}

# Define el modo por defecto cuando no se indique explícitamente.
MODO_PROMPT_POR_DEFECTO = "completo"

# Define el marcador obligatorio para inyectar el JSON de auditoría.
PLACEHOLDER_DATOS_JSON = "{datos_json}"

# Define patrones de negación GSC que no deben aparecer si hay datos reales.
PATRONES_NEGACION_GSC = {
    "no se proporcionan datos específicos de gsc",
    "no se proporcionan datos de gsc",
    "no hay datos de gsc",
    "no se dispone de datos de gsc",
    "sin datos de search console",
    "sin datos de gsc",
}

# Define métricas válidas para considerar PageSpeed como utilizable.
METRICAS_PAGESPEED_VALIDAS = (
    "performance_score",
    "accessibility_score",
    "best_practices_score",
    "seo_score",
    "lcp",
    "cls",
    "inp",
    "fcp",
    "tbt",
    "speed_index",
)


# Cachea el módulo Gemini una vez resuelto para evitar import dinámico repetitivo.
_MODULO_GENAI = None


# Resuelve el módulo de Gemini de forma perezosa para evitar fallos en import global.
def _obtener_modulo_gemini():
    """Devuelve el módulo de Gemini con carga opcional y caché local de proceso."""

    global _MODULO_GENAI

    # Reutiliza módulo previamente resuelto en este proceso.
    if _MODULO_GENAI is not None:
        return _MODULO_GENAI

    try:
        # Usa import local idiomático para dependencias opcionales.
        from google import genai as modulo_genai
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Dependencia opcional no disponible: instala `google-genai` para habilitar la integración Gemini."
        ) from exc

    _MODULO_GENAI = modulo_genai
    return _MODULO_GENAI


# Resuelve el cliente de Google Gemini de forma perezosa para evitar fallos en import global.
def _crear_cliente_gemini(api_key: str):
    """Crea un cliente de Gemini resolviendo la dependencia en tiempo de uso."""

    return _obtener_modulo_gemini().Client(api_key=api_key)


# Define fallback interno alineado 1:1 con el archivo editable del repositorio.
PROMPT_IA_FALLBACK = """Actúa como consultor SEO senior de agencia, especializado en crecimiento orgánico basado en datos reales.
Tu objetivo no es describir datos, sino analizarlos, cruzarlos y priorizar acciones que generen impacto directo en visibilidad, tráfico y negocio.
Redacta en español profesional, natural y claro.
Puedes usar emojis de forma moderada y estratégica para mejorar la legibilidad, especialmente en títulos y elementos clave, pero sin abusar.
No uses Markdown ni símbolos como **, ### o ---.
Usa únicamente los datos proporcionados. No inventes información ni menciones herramientas no activas.

IMPORTANTE:
- Prioriza impacto sobre cantidad de incidencias.
- Agrupa problemas similares.
- Da prioridad a páginas con datos reales de Search Console (impresiones, CTR, posición).
- Relaciona siempre datos técnicos con impacto SEO real.
- Evita listados largos sin contexto.
- Piensa como un consultor que tiene que mejorar resultados, no como un auditor técnico.

Debes cruzar información entre:
- SEO técnico
- contenido
- rendimiento
- Google Search Console

REGLAS DE CONSISTENCIA OBLIGATORIAS (NO INCUMPLIR):
- Lee y respeta estas banderas del JSON: gsc_activo, pagespeed_activo, fuentes_activas, fuentes_fallidas, usar_seccion_gsc.
- Usa también contexto_control como fuente prioritaria de verificación.
- Si gsc_activo=true o "search_console" aparece en fuentes_activas:
  - está prohibido afirmar que faltan datos de GSC/Search Console.
  - debes incluir insights y oportunidades de visibilidad orgánica real con los datos existentes.
- Si gsc_activo=false:
  - indica de forma explícita y breve que no hay datos de Search Console en esta ejecución.
- Si pagespeed_activo=false:
  - evita recomendaciones específicas de métricas de rendimiento no disponibles.
- No uses frases plantilla genéricas que contradigan el JSON real.

ESTRUCTURA OBLIGATORIA EXACTA:
Resumen ejecutivo:
- Explica el estado general del SEO del sitio.
- Indica si el problema principal es técnico, contenido o estrategia.
- Resume el potencial de crecimiento.
- Destaca oportunidades claras basadas en datos reales.
- Usa 2–3 emojis estratégicos.

Hallazgos críticos 🚨:
- Incluye solo problemas que afectan directamente al posicionamiento.
- Prioriza los que impactan en páginas con tráfico o impresiones.
- Agrupa problemas similares.
- Explica impacto real en SEO.

Quick wins ⚡:
- Selecciona entre 3 y 7 acciones.
- Deben ser de alto impacto y bajo esfuerzo.
- Basadas en datos reales (GSC si existe).
- Formato claro:
  - Acción:
  - Impacto:
  - Esfuerzo:
  - Resultado esperado:

Acciones técnicas ⚙️:
- Solo mejoras técnicas relevantes.
- Priorizadas por impacto real.
- Evita ruido.

Acciones de contenido 🧠:
- Evalúa calidad del contenido.
- Detecta thin content y falta de enfoque SEO.
- Relaciona con datos de GSC si es posible.
- Propón mejoras concretas.

Rendimiento y experiencia 🚀:
- Analiza PageSpeed y métricas.
- Explica impacto en SEO.
- Prioriza problemas reales.

Oportunidades SEO (GSC) 📈:
Analiza datos de Search Console.
Detecta:
- páginas con muchas impresiones y bajo CTR
- páginas en posición 4–15
- queries relevantes
- contenido desaprovechado
- Explica oportunidades claras y accionables.

Roadmap 🗺️:
Dividir en:
- Corto plazo:
  - quick wins y correcciones críticas
- Medio plazo:
  - optimización de páginas con potencial
  - mejora de CTR
  - mejora de contenido
- Largo plazo:
  - estrategia SEO
  - arquitectura
  - crecimiento orgánico

Datos de auditoría en JSON:
{datos_json}
"""


# Resuelve ruta de prompt por modo con fallback a informe general.
def resolver_ruta_prompt_ia(modo: str) -> Path:
    """Obtiene ruta del prompt modular priorizando `prompts/` y compatibilidad legacy."""

    # Normaliza modo para evitar errores por mayúsculas o espacios.
    modo_normalizado = (modo or MODO_PROMPT_POR_DEFECTO).strip().lower()

    # Obtiene nombre de archivo para el modo solicitado.
    nombre_prompt = MAPA_PROMPTS_POR_MODO.get(modo_normalizado, MAPA_PROMPTS_POR_MODO[MODO_PROMPT_POR_DEFECTO])

    # Guarda nombre de archivo por defecto para fallback controlado.
    nombre_prompt_default = MAPA_PROMPTS_POR_MODO[MODO_PROMPT_POR_DEFECTO]

    # Define rutas candidatas en orden de prioridad funcional.
    rutas_candidatas = [
        RUTA_CARPETA_PROMPTS / nombre_prompt,
        RUTA_CARPETA_PROMPTS / nombre_prompt_default,
        RUTA_PROMPT_UNICO_LEGACY,
    ]

    # Elimina duplicados manteniendo el orden para evitar comprobaciones repetidas.
    rutas_unicas = list(dict.fromkeys(rutas_candidatas))

    # Devuelve la primera ruta existente dentro del orden definido.
    for ruta in rutas_unicas:
        if ruta.is_file():
            return ruta

    # Devuelve fallback final al prompt modular por defecto aunque no exista en disco.
    return RUTA_CARPETA_PROMPTS / nombre_prompt_default


# Carga la plantilla de prompt desde archivo externo para facilitar su edición.
def cargar_plantilla_prompt_ia(modo: str = MODO_PROMPT_POR_DEFECTO) -> str:
    """Lee la plantilla de prompt según modo con fallback seguro."""

    # Resuelve ruta final del prompt en función del modo de ejecución.
    ruta_prompt = resolver_ruta_prompt_ia(modo)

    # Intenta leer el prompt externo configurable por el equipo.
    try:
        # Verifica que la ruta sea un archivo regular.
        if ruta_prompt.is_file():
            # Devuelve el contenido tal cual para máxima editabilidad.
            return ruta_prompt.read_text(encoding="utf-8")
    except OSError:
        # Ignora errores de sistema y aplica fallback seguro.
        pass

    # Usa plantilla interna si el archivo externo no está disponible o no se puede leer.
    return PROMPT_IA_FALLBACK


# Inserta los datos sin evaluar otras llaves literales del prompt editable.
def construir_prompt_ia(plantilla_prompt: str, datos: dict) -> str:
    """Compone el prompt final validando el marcador obligatorio de datos."""

    # Exige marcador para evitar llamadas IA sin contexto técnico.
    if PLACEHOLDER_DATOS_JSON not in plantilla_prompt:
        # Lanza error explícito para evitar salidas ambiguas o genéricas.
        raise ValueError("La plantilla de prompt debe incluir el marcador {datos_json}.")

    # Serializa datos SEO conservando caracteres en español.
    datos_json = json.dumps(datos, ensure_ascii=False)

    # Reemplaza solo el marcador previsto sin usar str.format.
    return plantilla_prompt.replace(PLACEHOLDER_DATOS_JSON, datos_json, 1)


# Construye un resumen optimizado para consumo eficiente de tokens en IA.
def construir_contexto_ia(resultado: ResultadoAuditoria, max_muestras: int) -> dict:
    """
    Crea un contexto agregado y limitado para reducir coste de tokens.
    """

    # Inicializa acumuladores de hallazgos por tipo y severidad.
    contador_problemas: Counter[str] = Counter()

    # Inicializa acumuladores de severidad para visión ejecutiva.
    contador_severidad: Counter[str] = Counter()

    # Inicializa lista con incidencias por URL para ranking.
    urls_con_problemas: list[tuple[str, int]] = []

    # Recorre cada resultado para consolidar métricas globales.
    for item in resultado.resultados:
        # Cuenta el número de hallazgos detectados por URL.
        total_hallazgos_url = len(item.hallazgos)

        # Añade la URL y su volumen de incidencias al ranking.
        urls_con_problemas.append((item.url, total_hallazgos_url))

        # Recorre hallazgos para contar descripciones y severidades.
        for hallazgo in item.hallazgos:
            # Incrementa la frecuencia de cada tipo de problema textual.
            contador_problemas[hallazgo.descripcion] += 1

            # Incrementa la frecuencia de cada severidad clasificada.
            contador_severidad[hallazgo.severidad] += 1

    # Ordena URLs por mayor número de incidencias.
    top_urls = sorted(urls_con_problemas, key=lambda item: item[1], reverse=True)

    # Construye quick wins basados en esfuerzo bajo y mayor impacto.
    quick_wins = []

    # Recorre resultados para detectar incidencias de alto potencial.
    for item in resultado.resultados:
        # Recorre hallazgos de la URL actual.
        for hallazgo in item.hallazgos:
            # Filtra incidencias de esfuerzo bajo y potencial relevante.
            if hallazgo.esfuerzo == "Bajo" and hallazgo.impacto in {"Muy alto", "Alto", "Medio"}:
                # Añade la incidencia al conjunto de quick wins.
                quick_wins.append({"url": item.url, "problema": hallazgo.descripcion, "recomendacion": hallazgo.recomendacion})

    # Resume resultados de rendimiento para minimizar tokens.
    resumen_rendimiento = []

    # Recorre resultados de rendimiento disponibles.
    for item in resultado.rendimiento[:max_muestras]:
        # Añade solo métricas necesarias para narrativa ejecutiva.
        resumen_rendimiento.append(
            {
                "url": item.url,
                "estrategia": item.estrategia,
                "performance_score": item.performance_score,
                "seo_score": item.seo_score,
                "lcp": item.lcp,
                "cls": item.cls,
                "inp": item.inp,
                "oportunidades": [oportunidad.titulo for oportunidad in item.oportunidades[:3]],
            }
        )

    # Deduplica quick wins por combinación URL-problema para ahorrar tokens.
    quick_wins_deduplicados = list({f"{item['url']}|{item['problema']}": item for item in quick_wins}.values())

    # Resume métricas GSC para reforzar consistencia contextual del prompt.
    gsc_resumen = {
        "paginas": len(resultado.search_console.paginas),
        "queries": len(resultado.search_console.queries),
        "clics_totales": round(sum(item.clicks for item in resultado.search_console.paginas), 2),
        "impresiones_totales": round(sum(item.impresiones for item in resultado.search_console.paginas), 2),
    }

    # Detecta si GSC trae filas utilizables para narrativa y recomendaciones.
    gsc_con_datos_utiles = bool(resultado.search_console.paginas or resultado.search_console.queries)

    # Marca GSC como activo solo con datos útiles o fuente validada por CLI.
    gsc_activo = bool(gsc_con_datos_utiles or "search_console" in resultado.fuentes_activas)

    # Detecta filas de PageSpeed con métricas reales y sin errores de ejecución.
    pagespeed_con_metricas_validas = any(
        any(getattr(item, metrica) is not None for metrica in METRICAS_PAGESPEED_VALIDAS) and not item.error for item in resultado.rendimiento
    )

    # Marca PageSpeed activo solo cuando hay métricas útiles o fuente validada por CLI.
    pagespeed_activo = bool(pagespeed_con_metricas_validas or "pagespeed" in resultado.fuentes_activas)

    # Detecta si Analytics aporta páginas útiles en esta ejecución.
    analytics_activo = bool(resultado.analytics.activo and resultado.analytics.paginas)

    # Detecta si existen datos útiles de GSC para habilitar secciones dedicadas.
    usar_seccion_gsc = bool(gsc_activo and gsc_con_datos_utiles)

    # Devuelve el contexto agregado y limitado para IA.
    return {
        "cliente": resultado.cliente,
        "sitemap": resultado.sitemap,
        "fecha_ejecucion": resultado.fecha_ejecucion,
        "gestor": resultado.gestor,
        "fuentes_activas": resultado.fuentes_activas,
        "fuentes_fallidas": resultado.fuentes_fallidas,
        "gsc_activo": gsc_activo,
        "analytics_activo": analytics_activo,
        "pagespeed_activo": pagespeed_activo,
        "usar_seccion_gsc": usar_seccion_gsc,
        "contexto_control": {
            "gsc_activo": gsc_activo,
            "analytics_activo": analytics_activo,
            "pagespeed_activo": pagespeed_activo,
            "fuentes_activas": resultado.fuentes_activas,
            "fuentes_fallidas": resultado.fuentes_fallidas,
            "usar_seccion_gsc": usar_seccion_gsc,
        },
        "total_urls": resultado.total_urls,
        "total_incidencias": sum(contador_problemas.values()),
        "distribucion_severidad": dict(contador_severidad),
        "top_problemas": [{"problema": problema, "cantidad": cantidad} for problema, cantidad in contador_problemas.most_common(max_muestras)],
        "top_urls_afectadas": [{"url": url, "incidencias": incidencias} for url, incidencias in top_urls[:max_muestras]],
        "muestras_representativas": [
            {
                "url": item.url,
                "estado_http": item.estado_http,
                "redirecciona": item.redirecciona,
                "noindex": item.noindex,
                "hallazgos": [hallazgo.descripcion for hallazgo in item.hallazgos[:2]],
            }
            for item in resultado.resultados[:max_muestras]
        ],
        "quick_wins": quick_wins_deduplicados[:max_muestras],
        "rendimiento": resumen_rendimiento,
        "gsc": gsc_resumen,
        "pagespeed_estado": resultado.pagespeed_estado,
        "indexacion_rastreo": resultado.indexacion_rastreo,
        "scores": {
            "tecnico": resultado.score_tecnico,
            "contenido": resultado.score_contenido,
            "rendimiento": resultado.score_rendimiento,
            "global": resultado.seo_score_global,
        },
    }

# Normaliza contradicciones del texto IA respecto a disponibilidad real de GSC.
def validar_consistencia_resumen_ia(texto: str, datos_contexto: dict) -> str:
    """Elimina frases contradictorias sobre GSC y añade nota consistente cuando aplique."""

    # Obtiene bandera de actividad GSC desde contexto inyectado.
    gsc_activo = bool(datos_contexto.get("gsc_activo"))

    # Obtiene fuentes activas normalizadas para validación cruzada.
    fuentes_activas = datos_contexto.get("fuentes_activas")
    fuentes = fuentes_activas if isinstance(fuentes_activas, list) else []

    # Refuerza actividad GSC cuando la fuente está explícitamente activa.
    gsc_activo = bool(gsc_activo or "search_console" in fuentes)

    # Si GSC no está activo no aplica limpieza de contradicción.
    if not gsc_activo:
        # Devuelve texto original sin alteraciones.
        return texto

    # Divide texto en líneas para filtrar frases problemáticas.
    lineas_filtradas: list[str] = []

    # Recorre líneas del texto IA para eliminar negaciones erróneas.
    for linea in texto.splitlines():
        # Normaliza línea para comparación robusta.
        linea_normalizada = linea.lower().strip()

        # Descarta líneas que nieguen datos de GSC cuando sí hay fuente activa.
        if any(patron in linea_normalizada for patron in PATRONES_NEGACION_GSC):
            # Omite línea contradictoria.
            continue

        # Conserva línea válida.
        lineas_filtradas.append(linea)

    # Reconstruye texto tras filtrar contradicciones.
    texto_filtrado = "\n".join(lineas_filtradas).strip()

    # Evita inyectar nota cuando ya exista una mención correcta de GSC.
    if "search console" in texto_filtrado.lower() or "gsc" in texto_filtrado.lower():
        # Devuelve texto ya consistente.
        return texto_filtrado

    # Obtiene métricas GSC para nota de coherencia explícita.
    gsc_data = datos_contexto.get("gsc")
    gsc = gsc_data if isinstance(gsc_data, dict) else {}

    # Construye nota de consistencia basada en datos reales.
    nota_consistencia = (
        "Nota de consistencia: se incluyeron datos reales de Search Console en este análisis "
        f"(clics={gsc.get('clics_totales', 0)}, impresiones={gsc.get('impresiones_totales', 0)})."
    )

    # Devuelve texto final añadiendo la nota de contexto.
    return f"{texto_filtrado}\n\n{nota_consistencia}".strip()


# Realiza una llamada mínima para validar conectividad y modelo de IA.
def probar_conexion_ia(api_key: str, model_name: str) -> str:
    """
    Ejecuta una prueba barata de IA y devuelve un mensaje de estado.
    """

    # Valida la existencia de la clave API antes de iniciar la prueba.
    if not api_key:
        # Informa error de configuración de clave.
        raise ValueError("No se ha configurado GEMINI_API_KEY.")

    # Crea cliente de Gemini con la clave indicada.
    cliente = _crear_cliente_gemini(api_key)

    # Lanza una petición mínima para validar credenciales y modelo.
    respuesta = cliente.models.generate_content(model=model_name, contents="Responde solo con: OK")

    # Obtiene el texto plano de respuesta de forma segura.
    texto = (getattr(respuesta, "text", "") or "").strip()

    # Devuelve un mensaje claro para CLI.
    return texto or "Respuesta vacía"


# Convierte el resultado técnico en un resumen narrativo con IA.
def generar_resumen_ia(
    resultado: ResultadoAuditoria,
    api_key: str,
    model_name: str,
    max_muestras: int,
    modo_prompt: str = MODO_PROMPT_POR_DEFECTO,
    cache_dir: Path | None = None,
    cache_ttl_segundos: int = 0,
) -> str:
    """
    Genera un resumen ejecutivo SEO usando Google AI Studio.
    """

    # Valida que exista una clave de API antes de llamar al servicio externo.
    if not api_key:
        # Corta el flujo con un mensaje claro y no ambiguo.
        raise ValueError("No se ha configurado GEMINI_API_KEY.")

    # Instancia el cliente del SDK con la clave indicada por entorno.
    cliente = _crear_cliente_gemini(api_key)

    # Construye el contexto resumido de IA con límite de muestras.
    datos = construir_contexto_ia(resultado, max_muestras)

    # Normaliza el modo recibido para evitar valores vacíos o con espacios.
    modo_efectivo = (modo_prompt or "").strip().lower()

    # Añade modo efectivo para trazabilidad del sistema modular.
    datos["modo"] = modo_efectivo or MODO_PROMPT_POR_DEFECTO

    # Expone modo también dentro de contexto_control para validación robusta del prompt.
    contexto_control = datos.get("contexto_control")
    if isinstance(contexto_control, dict):
        contexto_control["modo"] = datos["modo"]

    # Revisa caché local cuando se habilite explícitamente.
    if cache_dir is not None:
        # Construye clave estable de la consulta IA.
        clave_cache = construir_clave_cache("ia", {"modelo": model_name, "modo": modo_prompt, "datos": datos})

        # Intenta recuperar respuesta previa dentro del TTL.
        respuesta_cache = leer_cache(cache_dir, clave_cache, cache_ttl_segundos)

        # Devuelve respuesta cacheada cuando exista.
        if isinstance(respuesta_cache, str) and respuesta_cache.strip():
            # Corrige contradicciones también en cache para mantener coherencia.
            return validar_consistencia_resumen_ia(respuesta_cache, datos)

    # Carga la plantilla de prompt desde archivo externo editable.
    plantilla_prompt = cargar_plantilla_prompt_ia(modo_prompt)

    # Inserta los datos de auditoría de forma segura en la plantilla.
    prompt_principal = construir_prompt_ia(plantilla_prompt, datos)

    # Construye contexto extra obligatorio antes del prompt modular principal.
    contexto_extra_prompt = {
        "gsc_activo": bool(datos.get("gsc_activo")),
        "analytics_activo": bool(datos.get("analytics_activo")),
        "pagespeed_activo": bool(datos.get("pagespeed_activo")),
        "fuentes_activas": datos.get("fuentes_activas", []),
        "modo": datos.get("modo", MODO_PROMPT_POR_DEFECTO),
    }

    # Serializa el contexto extra para inyectarlo al inicio del prompt final.
    contexto_extra_json = json.dumps(contexto_extra_prompt, ensure_ascii=False)

    # Compone prompt final con contexto extra previo y bloque principal.
    prompt = f"Contexto extra de ejecución (JSON):\n{contexto_extra_json}\n\n{prompt_principal}"

    # Ejecuta la generación del contenido con el modelo indicado.
    respuesta = cliente.models.generate_content(model=model_name, contents=prompt)

    # Obtiene texto final con fallback controlado.
    texto = getattr(respuesta, "text", "") or "No se pudo generar el informe con IA."

    # Corrige contradicciones de narrativa IA respecto al contexto real.
    texto = validar_consistencia_resumen_ia(texto, datos)

    # Guarda respuesta en caché local cuando se habilite.
    if cache_dir is not None:
        # Persiste texto para reutilización posterior.
        escribir_cache(cache_dir, clave_cache, texto)

    # Devuelve el texto generado de forma segura y directa.
    return texto
