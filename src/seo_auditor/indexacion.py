# Importa parser de URL para derivar robots.txt.
from urllib.parse import urlparse

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


# Resuelve disponibilidad real de advertools en tiempo de ejecución.
ADVERTOOLS_DISPONIBLE = importlib.util.find_spec("advertools") is not None

# Carga módulo advertools solo cuando exista en entorno.
adv = importlib.import_module("advertools") if ADVERTOOLS_DISPONIBLE else None


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

    # Normaliza el user-agent objetivo para comparar sin sesgos de formato.
    agente_objetivo = user_agent_objetivo.strip().lower()

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

        # Reinicia estado en líneas vacías o directivas desconocidas.
        if not directiva or directiva == "nan":
            # Evita arrastrar user-agents entre bloques no relacionados.
            agentes_activos = []

            # Limpia referencia de última directiva para próximo bloque.
            ultima_directiva = ""

            # Continúa con la siguiente fila útil.
            continue

        # Actualiza user-agent activo cuando se detecta bloque nuevo.
        if directiva == "user-agent":
            # Reinicia bloque cuando aparece un user-agent tras reglas previas.
            if ultima_directiva != "user-agent":
                # Limpia agentes para evitar mezcla de bloques.
                agentes_activos = []

            # Añade agente al bloque activo en minúsculas.
            agentes_activos.append(contenido.lower())

            # Actualiza última directiva procesada.
            ultima_directiva = directiva

            # Continúa con la siguiente fila.
            continue

        # Cierra bloque cuando aparezcan directivas globales ajenas al grupo.
        if directiva in {"sitemap", "host"}:
            # Limpia estado para evitar arrastre entre bloques.
            agentes_activos = []

        # Filtra solo disallow con contenido no vacío.
        if directiva == "disallow" and contenido:
            # Evalúa si el bloque aplica exactamente al user-agent objetivo.
            if agente_objetivo in agentes_activos:
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
