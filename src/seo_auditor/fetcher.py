# Importa utilidades XML para parsear sitemaps de forma robusta.
from xml.etree import ElementTree

# Importa cliente HTTP seguro y extendido.
import requests

# Importa el analizador HTML para extraer metadatos de páginas.
from bs4 import BeautifulSoup

# Importa tipos para definir firmas claras.
from typing import List, Tuple

# Importa la validación de URLs del proyecto.
from seo_auditor.utils import es_url_http_valida, normalizar_url


# Define el espacio de nombres estándar de sitemaps XML.
NAMESPACE = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


# Descarga contenido textual desde una URL con controles básicos.
def descargar_texto(url: str, timeout: int) -> Tuple[str, requests.Response]:
    """
    Descarga el contenido textual de una URL.

    Parameters
    ----------
    url : str
        Recurso HTTP o HTTPS a consultar.
    timeout : int
        Tiempo máximo de espera en segundos.

    Returns
    -------
    Tuple[str, requests.Response]
        Texto de la respuesta y objeto de respuesta HTTP.

    Raises
    ------
    ValueError
        Si la URL no es válida.
    requests.RequestException
        Si falla la petición HTTP.
    """

    # Verifica que la URL tenga un formato permitido antes de solicitarla.
    if not es_url_http_valida(url):
        # Frena el flujo antes de hacer una petición insegura o inútil.
        raise ValueError(f"La URL no es válida: {url}")

    # Ejecuta una petición GET permitiendo seguir redirecciones de forma controlada.
    respuesta = requests.get(
        # Envía la URL saneada por si incluye espacios accidentales.
        normalizar_url(url),
        # Define un agente de usuario identificable y neutro.
        headers={"User-Agent": "AuditorSeoPro/0.1"},
        # Aplica un timeout defensivo para no bloquear la ejecución.
        timeout=timeout,
        # Indica que se deben seguir redirecciones HTTP estándar.
        allow_redirects=True,
    )

    # Fuerza excepción si el código es 4xx o 5xx.
    respuesta.raise_for_status()

    # Devuelve el texto y la respuesta completa para usos avanzados.
    return respuesta.text, respuesta


# Extrae URLs de un sitemap o índice de sitemaps.
def extraer_urls_sitemap(url_sitemap: str, timeout: int, max_urls: int) -> List[str]:
    """
    Descarga y parsea un sitemap XML, incluyendo índices simples.

    Parameters
    ----------
    url_sitemap : str
        URL del sitemap XML.
    timeout : int
        Tiempo máximo de espera por petición.
    max_urls : int
        Límite total de URLs a devolver.

    Returns
    -------
    List[str]
        URLs únicas obtenidas del sitemap.
    """

    # Descarga el XML del sitemap principal.
    xml_texto, _ = descargar_texto(url_sitemap, timeout)

    # Parsea el contenido XML recibido.
    raiz = ElementTree.fromstring(xml_texto)

    # Inicializa la lista de URLs consolidadas.
    urls: List[str] = []

    # Detecta si el XML es un índice de sitemaps.
    if raiz.tag.endswith("sitemapindex"):
        # Recorre cada sitemap hijo declarado en el índice.
        for nodo in raiz.findall("sm:sitemap", NAMESPACE):
            # Obtiene la URL del sitemap hijo desde el nodo `loc`.
            loc = nodo.findtext("sm:loc", default="", namespaces=NAMESPACE).strip()

            # Ignora nodos vacíos o inválidos para mantener robustez.
            if not es_url_http_valida(loc):
                # Continúa con el siguiente sitemap hijo válido.
                continue

            # Llama recursivamente para extraer URLs del sitemap hijo.
            urls.extend(extraer_urls_sitemap(loc, timeout, max_urls))

            # Detiene el proceso si ya se alcanzó el máximo permitido.
            if len(urls) >= max_urls:
                # Devuelve el subconjunto ya consolidado y limitado.
                return list(dict.fromkeys(urls))[:max_urls]

    # Gestiona el caso de un sitemap tradicional de URLs.
    elif raiz.tag.endswith("urlset"):
        # Recorre cada URL declarada dentro del sitemap.
        for nodo in raiz.findall("sm:url", NAMESPACE):
            # Lee el contenido del nodo `loc` con seguridad.
            loc = nodo.findtext("sm:loc", default="", namespaces=NAMESPACE).strip()

            # Añade solo URLs válidas para no contaminar el análisis.
            if es_url_http_valida(loc):
                # Normaliza la URL antes de almacenarla para evitar duplicados triviales.
                urls.append(normalizar_url(loc))

            # Detiene la lectura al alcanzar el límite defensivo.
            if len(urls) >= max_urls:
                # Sale del bucle sin seguir leyendo más URLs.
                break

    # Elimina duplicados preservando el orden original de descubrimiento.
    return list(dict.fromkeys(urls))[:max_urls]


# Descarga una página y extrae señales SEO básicas.
def obtener_metadatos_html(url: str, timeout: int) -> Tuple[requests.Response, BeautifulSoup]:
    """
    Descarga una página y devuelve la respuesta HTTP junto al árbol HTML.

    Parameters
    ----------
    url : str
        URL de la página a analizar.
    timeout : int
        Tiempo máximo de espera por petición.

    Returns
    -------
    Tuple[requests.Response, BeautifulSoup]
        Respuesta HTTP y documento HTML parseado.
    """

    # Lanza una petición HTTP con seguimiento de redirecciones activado.
    respuesta = requests.get(
        # Usa la URL indicada por el llamador.
        url,
        # Define un agente de usuario propio para facilitar trazabilidad.
        headers={"User-Agent": "AuditorSeoPro/0.1"},
        # Aplica timeout defensivo.
        timeout=timeout,
        # Sigue redirecciones para conocer la URL final servida.
        allow_redirects=True,
    )

    # Crea el árbol DOM con el parser estándar de BeautifulSoup.
    html = BeautifulSoup(respuesta.text, "html.parser")

    # Devuelve la respuesta completa y el documento parseado.
    return respuesta, html
