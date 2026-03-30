# Importa expresiones regulares para validaciones seguras y explícitas.
import re

# Importa utilidades de fecha para metadatos reales de ejecución.
from datetime import UTC, datetime

# Importa utilidades de URL estándar del lenguaje.
from urllib.parse import urlparse

# Importa tipos para iteradores con progreso.
from typing import Iterable, Iterator, TypeVar


# Define una expresión regular conservadora para validar URLs HTTP y HTTPS.
URL_REGEX = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)

# Define tipo genérico para iteradores con tipado.
T = TypeVar("T")


# Valida que una URL use un esquema permitido y tenga dominio.
def es_url_http_valida(url: str) -> bool:
    """
    Valida si una cadena representa una URL HTTP o HTTPS razonable.
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
    """

    # Elimina espacios externos para estabilizar la entrada.
    url_limpia = url.strip()

    # Devuelve la URL sin la barra final cuando no es la raíz del dominio.
    return url_limpia[:-1] if url_limpia.endswith("/") and len(urlparse(url_limpia).path) > 1 else url_limpia


# Infiere el tipo funcional de una URL a partir de su ruta.
def inferir_tipo_url(url: str) -> str:
    """
    Intenta clasificar una URL según su ruta.
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


# Genera la fecha real de ejecución en formato ISO.
def fecha_ejecucion_iso() -> str:
    """
    Devuelve la fecha UTC real de ejecución en formato YYYY-MM-DD.
    """

    # Obtiene la fecha actual en UTC para evitar discrepancias horarias.
    return datetime.now(UTC).date().isoformat()


# Convierte una URL de dominio en un slug estable para carpetas.
def slug_dominio_desde_url(url: str) -> str:
    """
    Construye un slug de dominio limpio sin www ni TLD para rutas de salida.
    """

    # Extrae el host de la URL con normalización de minúsculas.
    host = urlparse(url).netloc.lower().strip()

    # Elimina prefijos comunes de subdominio público.
    host = host[4:] if host.startswith("www.") else host

    # Separa el host en partes para aislar el nombre base.
    partes = [parte for parte in host.split(".") if parte]

    # Elige el segmento principal del dominio antes del TLD.
    candidato = partes[-2] if len(partes) >= 2 else (partes[0] if partes else "sitio")

    # Sustituye caracteres no válidos por guiones para un slug seguro.
    slug = re.sub(r"[^a-z0-9]+", "-", candidato).strip("-")

    # Devuelve un valor de respaldo si tras limpieza queda vacío.
    return slug or "sitio"


# Infiere un nombre de cliente legible a partir del slug del dominio.
def inferir_cliente_desde_slug(slug: str) -> str:
    """
    Convierte un slug en nombre comercial legible.
    """

    # Sustituye guiones por espacios para visualización.
    texto = slug.replace("-", " ").strip()

    # Devuelve un valor por defecto si no hay contenido utilizable.
    return texto.title() if texto else "Cliente"


# Recorre una colección mostrando progreso textual en consola.
def iterar_con_progreso(items: Iterable[T], descripcion: str, unidad: str) -> Iterator[T]:
    """
    Itera elementos mostrando progreso simple y compatible sin dependencias externas.
    """

    # Convierte los elementos a lista para conocer el total.
    lista = list(items)

    # Calcula el total de elementos de la colección.
    total = len(lista)

    # Recorre cada elemento con índice para dibujar avance.
    for indice, item in enumerate(lista, start=1):
        # Muestra progreso en una sola línea para no ensuciar la salida.
        print(f"\r{descripcion}: {indice}/{total} {unidad}", end="")

        # Entrega elemento actual al consumidor.
        yield item

    # Cierra la línea de progreso al completar la iteración.
    if total > 0:
        print("")
