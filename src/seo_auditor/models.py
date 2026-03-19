# Importa utilidades para crear modelos de datos simples y seguros.
from dataclasses import dataclass, field

# Importa tipos estándar para mejorar legibilidad y validación estática.
from typing import List, Optional


# Define la estructura de una incidencia SEO detectada durante la auditoría.
@dataclass(slots=True)
class HallazgoSeo:
    """
    Representa un problema o recomendación SEO detectada en una URL.

    Parameters
    ----------
    tipo : str
        Categoría del hallazgo, por ejemplo `indexación` o `contenido`.
    severidad : str
        Nivel de prioridad, normalmente `alta`, `media` o `baja`.
    descripcion : str
        Explicación breve del problema detectado.
    recomendacion : str
        Acción concreta recomendada para resolver el problema.
    """

    # Guarda la categoría funcional del hallazgo.
    tipo: str

    # Guarda la prioridad de negocio o técnica del hallazgo.
    severidad: str

    # Guarda la descripción breve del problema detectado.
    descripcion: str

    # Guarda la acción recomendada para corregir el problema.
    recomendacion: str


# Define la estructura de datos de una URL auditada.
@dataclass(slots=True)
class ResultadoUrl:
    """
    Representa el resultado técnico de analizar una URL.

    Parameters
    ----------
    url : str
        URL auditada.
    tipo : str
        Tipo inferido de URL, por ejemplo `page`, `post` o `category`.
    estado_http : int
        Código de estado HTTP final observado.
    redirecciona : bool
        Indica si la URL respondió con redirección.
    url_final : str
        URL final tras seguir redirecciones.
    title : str
        Contenido del título HTML si existe.
    h1 : str
        Primer H1 detectado si existe.
    meta_description : str
        Meta descripción detectada si existe.
    canonical : str | None
        Canonical declarada en la página si existe.
    noindex : bool
        Indica si la página declara noindex.
    hallazgos : List[HallazgoSeo]
        Lista de incidencias detectadas.
    error : str | None
        Mensaje controlado de error técnico, sin secretos.
    """

    # Guarda la URL original analizada.
    url: str

    # Guarda el tipo lógico de URL inferido a partir del sitemap o de la ruta.
    tipo: str

    # Guarda el código HTTP obtenido al final de la petición.
    estado_http: int

    # Indica si hubo redirección durante la descarga.
    redirecciona: bool

    # Guarda la URL final obtenida tras seguir redirecciones.
    url_final: str

    # Guarda el contenido del título si se ha podido extraer.
    title: str

    # Guarda el primer encabezado H1 detectado.
    h1: str

    # Guarda la meta descripción detectada.
    meta_description: str

    # Guarda la canonical encontrada, si existe.
    canonical: Optional[str]

    # Indica si la página está marcada como noindex.
    noindex: bool

    # Guarda todos los hallazgos detectados para la URL.
    hallazgos: List[HallazgoSeo] = field(default_factory=list)

    # Guarda un error controlado si la auditoría de la URL falló.
    error: Optional[str] = None


# Define la estructura global del resultado de una ejecución.
@dataclass(slots=True)
class ResultadoAuditoria:
    """
    Contiene el resultado consolidado de una auditoría SEO.

    Parameters
    ----------
    sitemap : str
        Sitemap origen de la auditoría.
    total_urls : int
        Número total de URLs consideradas.
    resultados : List[ResultadoUrl]
        Resultados por URL.
    resumen_ia : str | None
        Texto opcional enriquecido por IA.
    """

    # Guarda el sitemap usado como origen de datos.
    sitemap: str

    # Guarda el total de URLs incluidas en la ejecución.
    total_urls: int

    # Guarda los resultados por URL.
    resultados: List[ResultadoUrl]

    # Guarda el informe narrativo opcional generado por IA.
    resumen_ia: Optional[str] = None
