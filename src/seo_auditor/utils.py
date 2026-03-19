# Importa expresiones regulares para validaciones seguras y explícitas.
import re

# Importa utilidades de URL estándar del lenguaje.
from urllib.parse import urlparse


# Define una expresión regular conservadora para validar URLs HTTP y HTTPS.
URL_REGEX = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)


# Valida que una URL use un esquema permitido y tenga dominio.
def es_url_http_valida(url: str) -> bool:
    """
    Valida si una cadena representa una URL HTTP o HTTPS razonable.

    Parameters
    ----------
    url : str
        Valor a validar.

    Returns
    -------
    bool
        `True` si la URL es válida y `False` en caso contrario.

    Security
    --------
    La validación reduce el riesgo de procesar entradas no previstas.
    """

    # Comprueba primero que la entrada sea texto no vacío.
    if not isinstance(url, str) or not url.strip():
        # Devuelve falso cuando la entrada no es segura o útil.
        return False

    # Elimina espacios de cortesía para evitar falsos negativos triviales.
    url_limpia = url.strip()

    # Descarta entradas que no cumplan el patrón básico.
    if not URL_REGEX.match(url_limpia):
        # Devuelve falso cuando la estructura es claramente incorrecta.
        return False

    # Parsea la URL para validar sus componentes principales.
    resultado = urlparse(url_limpia)

    # Devuelve verdadero solo si el esquema y el dominio existen.
    return resultado.scheme in {"http", "https"} and bool(resultado.netloc)


# Normaliza una URL eliminando espacios innecesarios y barras finales redundantes.
def normalizar_url(url: str) -> str:
    """
    Normaliza una URL de forma conservadora para comparación interna.

    Parameters
    ----------
    url : str
        URL a normalizar.

    Returns
    -------
    str
        URL normalizada.
    """

    # Elimina espacios externos para estabilizar la entrada.
    url_limpia = url.strip()

    # Devuelve la URL sin la barra final cuando no es la raíz del dominio.
    return url_limpia[:-1] if url_limpia.endswith("/") and len(urlparse(url_limpia).path) > 1 else url_limpia


# Infiere el tipo funcional de una URL a partir de su ruta.
def inferir_tipo_url(url: str) -> str:
    """
    Intenta clasificar una URL según su ruta.

    Parameters
    ----------
    url : str
        URL a clasificar.

    Returns
    -------
    str
        Tipo lógico estimado.
    """

    # Obtiene solo la parte de ruta para analizarla de forma aislada.
    ruta = urlparse(url).path.lower()

    # Devuelve `category` si la ruta parece de categoría de WordPress.
    if "/category/" in ruta:
        # Informa de que la URL pertenece a una taxonomía de categoría.
        return "category"

    # Devuelve `tag` si la ruta parece de etiqueta de WordPress.
    if "/tag/" in ruta:
        # Informa de que la URL pertenece a una taxonomía de etiquetas.
        return "tag"

    # Devuelve `feed` si la ruta apunta a un feed.
    if ruta.endswith("/feed/") or ruta.endswith("/feed"):
        # Clasifica el recurso como feed y no como página de negocio.
        return "feed"

    # Devuelve `post` si la ruta contiene un patrón de fecha típico de WordPress.
    if re.search(r"/\d{4}/\d{2}/\d{2}/", ruta):
        # Clasifica la URL como entrada de blog.
        return "post"

    # Devuelve `page` para el resto de casos conocidos.
    return "page"
