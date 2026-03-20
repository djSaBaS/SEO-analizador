# Importa utilidades para parsear URL de forma segura.
from urllib.parse import urlparse

# Importa cliente HTTP para consultar la API pública de Google.
import requests

# Importa modelos de rendimiento tipados.
from seo_auditor.models import OportunidadRendimiento, ResultadoRendimiento


# Define endpoint oficial de PageSpeed Insights v5.
ENDPOINT_PAGESPEED = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


# Convierte un score de Lighthouse de 0-1 a escala 0-100.
def _score_a_100(valor: object) -> float | None:
    """
    Normaliza score numérico de Lighthouse a escala porcentual.
    """

    # Devuelve nulo cuando el valor no exista.
    if valor is None:
        # Retorna None cuando el score no esté disponible.
        return None

    # Verifica que el score pueda convertirse a flotante.
    if not isinstance(valor, (int, float)):
        # Retorna None cuando el dato no sea numérico.
        return None

    # Convierte el score a escala 0-100 con redondeo estándar.
    return round(float(valor) * 100.0, 1)


# Obtiene una métrica desde el bloque de auditorías de Lighthouse.
def _obtener_metrica(auditorias: dict, clave: str) -> str | None:
    """
    Extrae un valor de métrica textual para mostrar en informes.
    """

    # Obtiene el nodo de auditoría solicitado.
    nodo = auditorias.get(clave, {})

    # Devuelve el valor textual cuando esté disponible.
    return nodo.get("displayValue") if isinstance(nodo, dict) else None


# Infiere severidad desde ahorro estimado en milisegundos.
def _inferir_severidad(ahorro_ms: float) -> str:
    """
    Clasifica una oportunidad de rendimiento según ahorro potencial.
    """

    # Devuelve crítica para ahorro muy alto.
    if ahorro_ms >= 1200:
        # Marca la severidad más alta.
        return "crítica"

    # Devuelve alta para ahorro alto.
    if ahorro_ms >= 600:
        # Marca prioridad alta.
        return "alta"

    # Devuelve media para ahorro moderado.
    if ahorro_ms >= 250:
        # Marca prioridad media.
        return "media"

    # Devuelve baja para ahorro pequeño.
    return "baja"


# Extrae oportunidades Lighthouse con ahorro estimado.
def _extraer_oportunidades(auditorias: dict, max_oportunidades: int) -> list[OportunidadRendimiento]:
    """
    Convierte auditorías de tipo oportunidad en una lista compacta y útil.
    """

    # Inicializa la lista de salida de oportunidades.
    oportunidades: list[OportunidadRendimiento] = []

    # Recorre todas las auditorías devueltas por Lighthouse.
    for identificador, nodo in auditorias.items():
        # Descarta entradas no válidas.
        if not isinstance(nodo, dict):
            # Continúa con la siguiente auditoría.
            continue

        # Obtiene el ahorro potencial de milisegundos si existe.
        ahorro_ms = float(nodo.get("numericValue", 0.0) or 0.0)

        # Obtiene la descripción completa de la oportunidad.
        descripcion = str(nodo.get("description", "") or "").strip()

        # Descarta auditorías que no representen una oportunidad accionable.
        if ahorro_ms <= 0 or not descripcion:
            # Continúa con la siguiente auditoría.
            continue

        # Construye una instancia tipada de oportunidad.
        oportunidades.append(
            OportunidadRendimiento(
                id_oportunidad=identificador,
                titulo=str(nodo.get("title", identificador)).strip(),
                descripcion=descripcion,
                ahorro_estimado=nodo.get("displayValue", f"{int(ahorro_ms)} ms"),
                severidad=_inferir_severidad(ahorro_ms),
            )
        )

    # Ordena oportunidades por severidad y por mayor ahorro implícito.
    oportunidades_ordenadas = sorted(oportunidades, key=lambda item: {"crítica": 0, "alta": 1, "media": 2, "baja": 3}.get(item.severidad, 4))

    # Devuelve un subconjunto limitado para evitar ruido.
    return oportunidades_ordenadas[:max_oportunidades]


# Extrae métricas de campo desde loadingExperience cuando existan.
def _extraer_metricas_campo(datos_json: dict) -> tuple[str | None, str | None, str | None]:
    """
    Obtiene métricas CrUX públicas incluidas por PageSpeed en la respuesta.
    """

    # Obtiene el bloque de experiencia real del usuario.
    experiencia = datos_json.get("loadingExperience", {})

    # Obtiene métricas de campo por clave.
    metricas = experiencia.get("metrics", {}) if isinstance(experiencia, dict) else {}

    # Extrae percentil de LCP cuando exista.
    lcp = metricas.get("LARGEST_CONTENTFUL_PAINT_MS", {}).get("percentile")

    # Extrae percentil de CLS cuando exista.
    cls = metricas.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {}).get("percentile")

    # Extrae percentil de INP cuando exista.
    inp = metricas.get("INTERACTION_TO_NEXT_PAINT", {}).get("percentile")

    # Devuelve métricas formateadas para salida homogénea.
    return (
        f"{lcp} ms" if isinstance(lcp, (int, float)) else None,
        str(round(float(cls) / 100.0, 3)) if isinstance(cls, (int, float)) else None,
        f"{inp} ms" if isinstance(inp, (int, float)) else None,
    )


# Ejecuta una consulta de PageSpeed Insights para URL y estrategia.
def analizar_pagespeed_url(url: str, api_key: str, estrategia: str, timeout: int) -> ResultadoRendimiento:
    """
    Consulta PageSpeed Insights y devuelve resultados normalizados por estrategia.
    """

    # Valida que la estrategia solicitada sea soportada.
    if estrategia not in {"mobile", "desktop"}:
        # Corta el flujo con un error explícito y accionable.
        raise ValueError("La estrategia de PageSpeed debe ser 'mobile' o 'desktop'.")

    # Construye parámetros de consulta de la API.
    parametros = {"url": url, "strategy": estrategia, "key": api_key}

    # Inicializa estructura mínima para errores controlados.
    resultado_error = ResultadoRendimiento(
        url=url,
        estrategia=estrategia,
        performance_score=None,
        accessibility_score=None,
        best_practices_score=None,
        seo_score=None,
        lcp=None,
        cls=None,
        inp=None,
        fcp=None,
        tbt=None,
        speed_index=None,
        campo_lcp=None,
        campo_cls=None,
        campo_inp=None,
    )

    # Ejecuta la llamada HTTP a la API pública.
    try:
        # Lanza petición GET a la API.
        respuesta = requests.get(ENDPOINT_PAGESPEED, params=parametros, timeout=timeout)

        # Fuerza excepción en códigos HTTP de error.
        respuesta.raise_for_status()

        # Convierte la respuesta JSON a diccionario.
        datos_json = respuesta.json()

        # Obtiene bloque principal Lighthouse.
        lighthouse = datos_json.get("lighthouseResult", {})

        # Obtiene categorías de score.
        categorias = lighthouse.get("categories", {}) if isinstance(lighthouse, dict) else {}

        # Obtiene auditorías detalladas.
        auditorias = lighthouse.get("audits", {}) if isinstance(lighthouse, dict) else {}

        # Extrae métricas de campo disponibles.
        campo_lcp, campo_cls, campo_inp = _extraer_metricas_campo(datos_json)

        # Devuelve resultado consolidado con métricas clave.
        return ResultadoRendimiento(
            url=url,
            estrategia=estrategia,
            performance_score=_score_a_100(categorias.get("performance", {}).get("score")),
            accessibility_score=_score_a_100(categorias.get("accessibility", {}).get("score")),
            best_practices_score=_score_a_100(categorias.get("best-practices", {}).get("score")),
            seo_score=_score_a_100(categorias.get("seo", {}).get("score")),
            lcp=_obtener_metrica(auditorias, "largest-contentful-paint"),
            cls=_obtener_metrica(auditorias, "cumulative-layout-shift"),
            inp=_obtener_metrica(auditorias, "interaction-to-next-paint"),
            fcp=_obtener_metrica(auditorias, "first-contentful-paint"),
            tbt=_obtener_metrica(auditorias, "total-blocking-time"),
            speed_index=_obtener_metrica(auditorias, "speed-index"),
            campo_lcp=campo_lcp,
            campo_cls=campo_cls,
            campo_inp=campo_inp,
            oportunidades=_extraer_oportunidades(auditorias, 6),
        )

    # Maneja error de red/API sin romper la ejecución completa.
    except Exception as exc:
        # Registra el error controlado en el objeto de salida.
        resultado_error.error = str(exc)

        # Devuelve resultado con error sin lanzar excepción aguas arriba.
        return resultado_error


# Detecta la home a partir del dominio base o del conjunto de URLs.
def detectar_home(url_sitemap: str, urls: list[str]) -> str:
    """
    Determina la URL home priorizando la raíz del dominio del sitemap.
    """

    # Obtiene componentes del sitemap.
    parseada = urlparse(url_sitemap)

    # Construye la raíz del dominio en HTTPS/HTTP original.
    home = f"{parseada.scheme}://{parseada.netloc}/"

    # Devuelve la home si existe ya en el sitemap.
    if home in urls:
        # Retorna coincidencia exacta encontrada.
        return home

    # Busca una URL con ruta raíz en el listado.
    for url in urls:
        # Verifica si la URL pertenece al mismo dominio y raíz.
        if urlparse(url).netloc == parseada.netloc and urlparse(url).path in {"", "/"}:
            # Retorna la URL detectada como home.
            return url

    # Devuelve la raíz inferida cuando no se encuentre en el sitemap.
    return home
