# Importa parser de URL para derivar robots.txt y parámetros.
from urllib.parse import parse_qsl, urlparse

# Importa expresiones regulares para matching robusto por segmentos.
import re

# Importa parser estándar de robots para evaluación precisa allow/disallow.
from urllib.robotparser import RobotFileParser

# Importa utilidades para dependencias opcionales.
import importlib

# Importa utilidades de descubrimiento de módulos.
import importlib.util

# Importa cliente HTTP para validaciones de disponibilidad.
import requests

# Importa utilidades internas de normalización y validación.
from seo_auditor.utils import es_url_http_valida, normalizar_url

# Importa modelos tipados para decisiones de indexación.
from seo_auditor.models import DecisionIndexacion, MetricaGscPagina, ResultadoUrl


# Resuelve disponibilidad real de advertools en tiempo de ejecución.
ADVERTOOLS_DISPONIBLE = importlib.util.find_spec("advertools") is not None

# Carga módulo advertools solo cuando exista en entorno.
adv = importlib.import_module("advertools") if ADVERTOOLS_DISPONIBLE else None

# Define patrones de URL normalmente no indexables.
PATRONES_NO_INDEXAR_URL = ["/gracias", "/thank", "/form", "/formulario", "/feed", "/page/", "/wp-json"]

# Define parámetros de tracking o sesión candidatos a exclusión.
PARAMETROS_NO_INDEXAR = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}

# Define frases habituales de confirmación no indexable.
FRASES_CONFIRMACION = {"gracias por", "thank you", "formulario enviado", "confirmación", "confirmacion", "suscripción confirmada", "suscripcion confirmada"}


# Deriva la URL de robots.txt a partir del sitemap base.
def _resolver_robots_url(sitemap_url: str) -> str:
    """Construye la ruta canónica de robots.txt para el dominio analizado."""

    # Parsea el sitemap para obtener esquema y host.
    parseada = urlparse(sitemap_url)

    # Devuelve robots.txt del dominio base.
    return f"{parseada.scheme}://{parseada.netloc}/robots.txt"


# Evalúa si una ruta está bloqueada por patrones básicos de robots.
def _esta_bloqueada_por_patrones(url: str, patrones_disallow: list[str]) -> bool:
    """Determina bloqueo simple mediante coincidencia de prefijo de ruta."""

    # Obtiene la ruta de la URL auditada.
    ruta_url = urlparse(url).path or "/"

    # Recorre cada patrón disallow detectado.
    for patron in patrones_disallow:
        # Limpia espacios para comparación robusta.
        patron_limpio = patron.strip()

        # Omite patrones vacíos.
        if not patron_limpio:
            # Continúa con el siguiente patrón válido.
            continue

        # Evalúa comodín global en robots.
        if patron_limpio == "/":
            # Marca bloqueo completo del dominio.
            return True

        # Evalúa coincidencia de prefijo de ruta.
        if ruta_url.startswith(patron_limpio):
            # Marca URL bloqueada por robots.
            return True

    # Devuelve no bloqueada cuando no hay coincidencias.
    return False


# Extrae patrones Disallow aplicables al user-agent objetivo desde advertools.
def _extraer_disallow_por_user_agent(robots_df, user_agent_objetivo: str = "*") -> list[str]:
    """Filtra directivas Disallow únicamente para bloques del user-agent objetivo."""

    # Inicializa lista de user-agents activos del bloque actual.
    agentes_activos: list[str] = []

    # Inicializa lista de patrones disallow aplicables.
    patrones_disallow: list[str] = []

    # Inicializa marcador de última directiva procesada.
    ultima_directiva = ""

    # Recorre filas respetando el orden del robots original.
    for _, fila in robots_df.iterrows():
        # Lee directiva normalizada de la fila.
        directiva = str(fila.get("directive", "")).strip().lower()

        # Lee contenido asociado a la directiva.
        contenido = str(fila.get("content", "")).strip()

        # Actualiza user-agent activo cuando se detecta bloque nuevo.
        if directiva == "user-agent":
            # Reinicia bloque cuando aparece un nuevo user-agent tras reglas previas.
            if ultima_directiva != "user-agent":
                # Limpia agentes para evitar mezcla de bloques.
                agentes_activos = []

            # Añade agente al bloque activo en minúsculas.
            agentes_activos.append(contenido.lower())

            # Actualiza última directiva procesada.
            ultima_directiva = directiva

            # Continúa con la siguiente fila.
            continue

        # Reinicia bloque cuando aparezcan directivas no asociadas a user-agent previo.
        if directiva in {"sitemap", "host"}:
            # Limpia estado para evitar arrastre entre bloques.
            agentes_activos = []

        # Filtra solo disallow con contenido no vacío.
        if directiva == "disallow" and contenido:
            # Evalúa si el bloque aplica al user-agent objetivo o wildcard.
            if user_agent_objetivo.lower() in agentes_activos or "*" in agentes_activos:
                # Añade patrón aplicable al conjunto final.
                patrones_disallow.append(contenido)

        # Actualiza última directiva tras procesar la fila.
        ultima_directiva = directiva

    # Devuelve patrones disallow filtrados por user-agent.
    return patrones_disallow


# Analiza indexación/rastreo usando robots y sitemap de forma tolerante.
def analizar_indexacion_rastreo(sitemap_url: str, urls_sitemap: list[str], timeout: int) -> dict[str, object]:
    """Devuelve un resumen de indexación y rastreo apto para informes ejecutivos."""

    # Inicializa estructura de respuesta por defecto.
    resumen: dict[str, object] = {
        "robots_url": "",
        "robots_disponible": False,
        "sitemap_valido": bool(urls_sitemap),
        "urls_bloqueadas": [],
        "incoherencias_sitemap_robots": [],
        "urls_huerfanas": [],
        "detalle_error": "",
    }

    # Evita análisis cuando sitemap no sea válido.
    if not es_url_http_valida(sitemap_url):
        # Registra error de parámetro.
        resumen["detalle_error"] = "Sitemap inválido para análisis de indexación."

        # Devuelve resumen mínimo seguro.
        return resumen

    # Resuelve URL de robots para el dominio objetivo.
    robots_url = _resolver_robots_url(sitemap_url)

    # Guarda URL de robots en el resumen.
    resumen["robots_url"] = robots_url

    # Intenta consultar robots para verificar disponibilidad real.
    try:
        # Ejecuta solicitud de robots.
        respuesta_robots = requests.get(robots_url, timeout=timeout)

        # Marca disponibilidad solo con HTTP exitoso.
        resumen["robots_disponible"] = respuesta_robots.status_code == 200
    except Exception as exc:
        # Registra error controlado de conectividad.
        resumen["detalle_error"] = f"No se pudo leer robots.txt: {exc}"

        # Devuelve resumen parcial sin romper ejecución.
        return resumen

    # Inicializa patrones disallow detectados para fallback.
    patrones_disallow: list[str] = []

    # Inicializa parser estándar de robots para evaluación precisa.
    parser_robots = RobotFileParser()

    # Carga contenido de robots en parser estándar.
    parser_robots.parse(respuesta_robots.text.splitlines())

    # Intenta parsear robots con advertools cuando esté disponible.
    if adv is not None:
        # Intenta parsear reglas robots con advertools.
        try:
            # Obtiene dataframe de reglas robots para el dominio.
            robots_df = adv.robotstxt_to_df(robots_url)

            # Filtra disallow aplicables al user-agent global.
            patrones_disallow = _extraer_disallow_por_user_agent(robots_df, "*")
        except Exception:
            # Mantiene flujo incluso si advertools no puede parsear robots.
            patrones_disallow = []

    # Inicializa acumuladores de bloqueo detectado.
    urls_bloqueadas: list[str] = []

    # Recorre URLs del sitemap para validar coherencia con robots.
    for url in urls_sitemap:
        # Evalúa bloqueo con parser estándar para respetar Allow/Disallow complejos.
        bloqueada_por_parser = not parser_robots.can_fetch("*", normalizar_url(url))

        # Evalúa bloqueo por patrones simples como fallback complementario.
        bloqueada_por_patron = _esta_bloqueada_por_patrones(normalizar_url(url), patrones_disallow)

        # Marca URL bloqueada cuando cualquiera de las dos validaciones lo confirme.
        if bloqueada_por_parser or bloqueada_por_patron:
            # Añade URL bloqueada al listado.
            urls_bloqueadas.append(url)

    # Guarda URLs bloqueadas en el resumen.
    resumen["urls_bloqueadas"] = urls_bloqueadas

    # Reutiliza lista bloqueada como incoherencia principal.
    resumen["incoherencias_sitemap_robots"] = list(urls_bloqueadas)

    # Devuelve resumen completo de indexación/rastreo.
    return resumen


# Construye índice rápido de métricas GSC por URL para reglas de visibilidad.
def _indice_gsc_por_url(metricas_gsc: list[MetricaGscPagina] | None) -> dict[str, MetricaGscPagina]:
    """Construye un índice por URL con métricas de Search Console."""

    # Inicializa índice vacío por defecto.
    indice: dict[str, MetricaGscPagina] = {}

    # Devuelve vacío cuando no hay métricas.
    if not metricas_gsc:
        # Retorna estructura vacía segura.
        return indice

    # Recorre métricas de GSC para indexarlas por URL.
    for fila in metricas_gsc:
        # Guarda fila en índice por URL canónica.
        indice[normalizar_url(fila.url)] = fila

    # Devuelve índice final para consulta rápida.
    return indice


# Evalúa coincidencia por segmentos de ruta para patrones no indexables.
def _ruta_coincide_patron_no_indexar(ruta: str, patron: str) -> bool:
    """Comprueba si un patrón no indexable aparece en un límite de segmento."""

    # Trata paginación explícita para evitar falsos positivos en slugs con /page.
    if patron == "/page/":
        # Exige segmento numérico tras /page/ como en archivos paginados.
        return re.search(r"(?:^|/)page/\d+(?:/|$)", ruta) is not None

    # Escapa patrón sin slash inicial para usarlo de forma segura en regex.
    patron_escapado = re.escape(patron.lstrip("/"))

    # Maneja patrón vacío sin clasificar masivamente.
    if not patron_escapado:
        # Evita marcar todas las rutas por un patrón ambiguo.
        return False

    # Construye regex anclada al inicio o límites de segmento de ruta.
    regex_segmento = rf"(?:^|/){patron_escapado}(?:/|$)"

    # Devuelve si existe coincidencia por límite de segmento.
    return re.search(regex_segmento, ruta) is not None


# Evalúa señales de URL para indexación inteligente.
def _evaluar_senales_url(url: str) -> list[str]:
    """Devuelve señales de exclusión o revisión detectadas en la URL."""

    # Inicializa colección de señales detectadas.
    senales: list[str] = []

    # Normaliza URL en minúsculas para matching robusto.
    url_normalizada = normalizar_url(url).lower()

    # Extrae la ruta para matching por segmentos.
    ruta = urlparse(url_normalizada).path or "/"

    # Recorre patrones directos de no indexación.
    for patron in PATRONES_NO_INDEXAR_URL:
        # Registra señal únicamente cuando el patrón coincide por segmentos.
        if _ruta_coincide_patron_no_indexar(ruta, patron):
            # Registra motivo por patrón de URL.
            senales.append(f"Patrón de URL detectado: {patron}")

    # Extrae query string para evaluar parámetros de tracking.
    query = urlparse(url_normalizada).query

    # Recorre pares clave-valor de la query.
    for nombre_parametro, _ in parse_qsl(query, keep_blank_values=True):
        # Marca parámetro cuando pertenezca al conjunto de tracking.
        if nombre_parametro in PARAMETROS_NO_INDEXAR or nombre_parametro.startswith("utm_"):
            # Registra motivo de parámetro no indexable.
            senales.append(f"Parámetro no canónico detectado: {nombre_parametro}")

    # Devuelve señales detectadas para la URL.
    return senales


# Evalúa señales de contenido y SEO de una URL auditada.
def _evaluar_senales_contenido_y_seo(item: ResultadoUrl) -> tuple[list[str], list[str]]:
    """Devuelve señales de no indexación y de revisión a partir del análisis técnico."""

    # Inicializa señales fuertes para no indexación.
    senales_no_indexar: list[str] = []

    # Inicializa señales moderadas para revisión.
    senales_revisar: list[str] = []

    # Detecta noindex como señal directa de exclusión.
    if item.noindex:
        # Añade motivo principal de exclusión.
        senales_no_indexar.append("Meta robots noindex detectada")

    # Detecta contenido extremadamente corto.
    if item.palabras < 120:
        # Añade señal de thin content severo.
        senales_revisar.append(f"Contenido muy corto ({item.palabras} palabras)")

    # Evalúa señales textuales de confirmación.
    texto_compuesto = f"{item.title} {item.h1} {item.texto_extraido}".lower()

    # Recorre frases de confirmación conocidas.
    for frase in FRASES_CONFIRMACION:
        # Marca páginas de confirmación transaccional.
        if frase in texto_compuesto:
            # Añade motivo de no indexación por confirmación.
            senales_no_indexar.append("Contenido de confirmación detectado")
            # Finaliza tras primera coincidencia.
            break

    # Marca ausencia de headings como revisión de calidad/indexación.
    if not item.h1.strip():
        # Añade motivo de revisión estructural.
        senales_revisar.append("Ausencia de heading principal (H1)")

    # Evalúa canonical potencialmente incoherente para revisión.
    if item.canonical and normalizar_url(item.canonical) != normalizar_url(item.url_final):
        # Añade motivo de revisión por canonical.
        senales_revisar.append("Canonical no autorreferente")

    # Recorre hallazgos para detectar señales de enlazado interno.
    for hallazgo in item.hallazgos:
        # Normaliza descripción para matching.
        descripcion = hallazgo.descripcion.lower()

        # Detecta pistas de enlazado interno débil.
        if "enlazado interno" in descripcion or "huérfana" in descripcion or "huerfana" in descripcion:
            # Añade motivo de revisión por discoverability.
            senales_revisar.append("Señal de enlazado interno débil")
            # Evita duplicados innecesarios.
            break

    # Devuelve señales consolidadas.
    return senales_no_indexar, senales_revisar


# Determina prioridad operativa según clasificación y señales.
def _prioridad_por_clasificacion(clasificacion: str, cantidad_motivos: int) -> str:
    """Devuelve prioridad de ejecución en formato alto/medio/bajo."""

    # Prioriza alto para exclusiones directas.
    if clasificacion == "NO_INDEXAR":
        # Devuelve prioridad alta por riesgo de indexación.
        return "Alta"

    # Prioriza media para revisiones con múltiples señales.
    if clasificacion == "REVISAR" and cantidad_motivos >= 2:
        # Devuelve prioridad media para casos con señales acumuladas.
        return "Media"

    # Devuelve prioridad baja en resto de casos.
    return "Baja"


# Genera decisiones de gestión de indexación inteligente por URL.
def generar_gestion_indexacion_inteligente(
    resultados: list[ResultadoUrl],
    metricas_gsc: list[MetricaGscPagina] | None = None,
) -> list[DecisionIndexacion]:
    """Clasifica URLs en INDEXABLE/REVISAR/NO_INDEXAR usando señales de URL, contenido, SEO y GSC."""

    # Construye índice rápido de GSC por URL.
    indice_gsc = _indice_gsc_por_url(metricas_gsc)

    # Inicializa colección de decisiones finales.
    decisiones: list[DecisionIndexacion] = []

    # Recorre resultados técnicos URL a URL.
    for item in resultados:
        # Calcula señales extraídas desde la propia URL.
        senales_url = _evaluar_senales_url(item.url)

        # Calcula señales derivadas de contenido y SEO.
        senales_no_indexar, senales_revisar = _evaluar_senales_contenido_y_seo(item)

        # Traslada señales de URL a la categoría de no indexación.
        senales_no_indexar.extend(senales_url)

        # Obtiene métricas GSC de la URL auditada normalizada cuando existan.
        metrica_gsc = indice_gsc.get(normalizar_url(item.url))

        # Reintenta lookup con URL final para tolerar redirecciones triviales.
        if metrica_gsc is None:
            # Busca la URL final normalizada en índice GSC.
            metrica_gsc = indice_gsc.get(normalizar_url(item.url_final))

        # Aplica regla de URL indexada sin impresiones.
        if metrica_gsc and metrica_gsc.impresiones == 0:
            # Añade señal de revisión por falta de visibilidad.
            senales_revisar.append("URL indexada sin impresiones en GSC")

        # Aplica regla de URL sin clics con impresiones.
        if metrica_gsc and metrica_gsc.impresiones > 0 and metrica_gsc.clicks == 0:
            # Añade señal de revisión por baja capacidad de atracción.
            senales_revisar.append("URL sin clics en GSC")

        # Determina clasificación final por precedencia.
        if senales_no_indexar:
            # Clasifica como no indexable ante señales fuertes.
            clasificacion = "NO_INDEXAR"
            # Define acción recomendada de exclusión.
            accion = "Aplicar/confirmar noindex, excluir de sitemap y reforzar canonicalización."
            # Selecciona motivos principales de no indexación.
            motivos = senales_no_indexar
        elif senales_revisar:
            # Clasifica como revisión pendiente.
            clasificacion = "REVISAR"
            # Define acción de mejora antes de indexar.
            accion = "Corregir señales SEO/contenido y validar rastreo antes de forzar indexación."
            # Selecciona motivos de revisión.
            motivos = senales_revisar
        else:
            # Clasifica como indexable cuando no hay señales negativas.
            clasificacion = "INDEXABLE"
            # Define acción de mantenimiento.
            accion = "Mantener indexación activa, enlazado interno y monitorización en GSC."
            # Define motivo de estado saludable.
            motivos = ["Sin señales de riesgo detectadas"]

        # Construye lista de motivos únicos para salida y prioridad consistentes.
        motivos_unicos = list(dict.fromkeys(motivos))

        # Construye motivo textual consolidado para exportación.
        motivo = "; ".join(motivos_unicos)

        # Calcula prioridad operativa final.
        prioridad = _prioridad_por_clasificacion(clasificacion, len(motivos_unicos))

        # Añade decisión final de la URL.
        decisiones.append(
            DecisionIndexacion(
                url=item.url,
                clasificacion=clasificacion,
                motivo=motivo,
                accion_recomendada=accion,
                prioridad=prioridad,
            )
        )

    # Devuelve todas las decisiones de gestión de indexación.
    return decisiones
