# Importa serialización JSON para enviar contexto técnico a la IA.
import json

# Importa contador para resumir hallazgos por frecuencia.
from collections import Counter

# Importa Path para caché local opcional y lectura de plantilla de prompt.
from pathlib import Path

# Importa el cliente oficial actual de Google Gemini.
from google import genai

# Importa utilidades de caché local reutilizable.
from seo_auditor.cache import construir_clave_cache, escribir_cache, leer_cache

# Importa el modelo de resultado global para tipado claro.
from seo_auditor.models import ResultadoAuditoria

# Define la ruta del archivo de prompt editable del proyecto.
RUTA_PROMPT_IA = Path(__file__).resolve().parents[2] / "Prompt" / "consulta_ia_prompt.txt"


# Define el marcador obligatorio para inyectar el JSON de auditoría.
PLACEHOLDER_DATOS_JSON = "{datos_json}"


# Define fallback interno con el mismo formato multilínea del archivo editable.
PROMPT_IA_FALLBACK = """Actúa como consultor SEO senior de agencia.
Redacta un informe en español profesional natural, sin frases vacías ni repeticiones.
Usa solo los datos proporcionados, sin inventar información.
No menciones fuentes no activas ni herramientas no conectadas.
No uses Markdown ni símbolos como **, ### o ---.
Estructura obligatoria exacta:
Resumen ejecutivo; Hallazgos críticos; Quick wins; Acciones técnicas; Acciones de contenido; Rendimiento y experiencia de usuario; Roadmap.
Datos de auditoría en JSON:
{datos_json}
"""


# Carga la plantilla de prompt desde archivo externo para facilitar su edición.
def cargar_plantilla_prompt_ia() -> str:
    """Lee la plantilla del prompt desde disco con fallback seguro."""

    # Intenta leer el prompt externo configurable por el equipo.
    try:
        # Verifica que la ruta sea un archivo regular.
        if RUTA_PROMPT_IA.is_file():
            # Devuelve el contenido tal cual para máxima editabilidad.
            return RUTA_PROMPT_IA.read_text(encoding="utf-8")
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

    # Devuelve el contexto agregado y limitado para IA.
    return {
        "cliente": resultado.cliente,
        "sitemap": resultado.sitemap,
        "fecha_ejecucion": resultado.fecha_ejecucion,
        "gestor": resultado.gestor,
        "fuentes_activas": resultado.fuentes_activas,
        "fuentes_fallidas": resultado.fuentes_fallidas,
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
        "pagespeed_estado": resultado.pagespeed_estado,
        "indexacion_rastreo": resultado.indexacion_rastreo,
        "scores": {
            "tecnico": resultado.score_tecnico,
            "contenido": resultado.score_contenido,
            "rendimiento": resultado.score_rendimiento,
            "global": resultado.seo_score_global,
        },
    }


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
    cliente = genai.Client(api_key=api_key)

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
    cliente = genai.Client(api_key=api_key)

    # Construye el contexto resumido de IA con límite de muestras.
    datos = construir_contexto_ia(resultado, max_muestras)

    # Revisa caché local cuando se habilite explícitamente.
    if cache_dir is not None:
        # Construye clave estable de la consulta IA.
        clave_cache = construir_clave_cache("ia", {"modelo": model_name, "datos": datos})

        # Intenta recuperar respuesta previa dentro del TTL.
        respuesta_cache = leer_cache(cache_dir, clave_cache, cache_ttl_segundos)

        # Devuelve respuesta cacheada cuando exista.
        if isinstance(respuesta_cache, str) and respuesta_cache.strip():
            # Retorna texto cacheado para ahorrar coste y latencia.
            return respuesta_cache

    # Carga la plantilla de prompt desde archivo externo editable.
    plantilla_prompt = cargar_plantilla_prompt_ia()

    # Inserta los datos de auditoría serializados en la plantilla.
    prompt = plantilla_prompt.format(datos_json=json.dumps(datos, ensure_ascii=False))

    # Ejecuta la generación del contenido con el modelo indicado.
    respuesta = cliente.models.generate_content(model=model_name, contents=prompt)

    # Obtiene texto final con fallback controlado.
    texto = getattr(respuesta, "text", "") or "No se pudo generar el informe con IA."

    # Guarda respuesta en caché local cuando se habilite.
    if cache_dir is not None:
        # Persiste texto para reutilización posterior.
        escribir_cache(cache_dir, clave_cache, texto)

    # Devuelve el texto generado de forma segura y directa.
    return texto
