# Importa utilidades para crear modelos de datos simples y seguros.
from dataclasses import dataclass, field

# Importa tipos estándar para mejorar legibilidad y validación estática.
from typing import List, Optional


# Define la estructura de una incidencia SEO detectada durante la auditoría.
@dataclass(slots=True)
class HallazgoSeo:
    """
    Representa un problema o recomendación SEO detectada en una URL.
    """

    # Guarda la categoría funcional del hallazgo.
    tipo: str

    # Guarda la prioridad de negocio o técnica del hallazgo.
    severidad: str

    # Guarda la descripción breve del problema detectado.
    descripcion: str

    # Guarda la acción recomendada para corregir el problema.
    recomendacion: str

    # Guarda el área propietaria de la incidencia.
    area: str

    # Guarda la estimación de impacto del hallazgo.
    impacto: str

    # Guarda la estimación de esfuerzo para resolución.
    esfuerzo: str

    # Guarda la prioridad recomendada de ejecución.
    prioridad: str


# Define la estructura de una oportunidad detectada por Lighthouse/PageSpeed.
@dataclass(slots=True)
class OportunidadRendimiento:
    """
    Representa una oportunidad accionable de optimización de rendimiento.
    """

    # Guarda el identificador técnico de la oportunidad.
    id_oportunidad: str

    # Guarda el título legible de la oportunidad.
    titulo: str

    # Guarda la descripción de negocio/técnica de la oportunidad.
    descripcion: str

    # Guarda ahorro estimado devuelto por Lighthouse cuando exista.
    ahorro_estimado: str

    # Guarda una severidad orientativa para seguimiento.
    severidad: str


# Define la estructura de resultados de PageSpeed por URL y estrategia.
@dataclass(slots=True)
class ResultadoRendimiento:
    """
    Almacena métricas de laboratorio y campo obtenidas desde PageSpeed.
    """

    # Guarda la URL analizada.
    url: str

    # Guarda la estrategia usada en la llamada (mobile o desktop).
    estrategia: str

    # Guarda el score de rendimiento en escala 0-100.
    performance_score: Optional[float]

    # Guarda el score de accesibilidad en escala 0-100.
    accessibility_score: Optional[float]

    # Guarda el score de buenas prácticas en escala 0-100.
    best_practices_score: Optional[float]

    # Guarda el score SEO en escala 0-100.
    seo_score: Optional[float]

    # Guarda la métrica LCP (laboratorio).
    lcp: Optional[str]

    # Guarda la métrica CLS (laboratorio).
    cls: Optional[str]

    # Guarda la métrica INP (laboratorio) cuando exista.
    inp: Optional[str]

    # Guarda la métrica FCP (laboratorio).
    fcp: Optional[str]

    # Guarda la métrica TBT (laboratorio) cuando exista.
    tbt: Optional[str]

    # Guarda la métrica Speed Index (laboratorio).
    speed_index: Optional[str]

    # Guarda la métrica de campo LCP cuando exista.
    campo_lcp: Optional[str]

    # Guarda la métrica de campo CLS cuando exista.
    campo_cls: Optional[str]

    # Guarda la métrica de campo INP cuando exista.
    campo_inp: Optional[str]

    # Guarda las oportunidades principales detectadas.
    oportunidades: List[OportunidadRendimiento] = field(default_factory=list)

    # Guarda un error controlado de consulta cuando ocurra.
    error: Optional[str] = None


# Define la estructura de datos de una URL auditada.
@dataclass(slots=True)
class ResultadoUrl:
    """
    Representa el resultado técnico de analizar una URL.
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
    """

    # Guarda el sitemap usado como origen de datos.
    sitemap: str

    # Guarda el total de URLs incluidas en la ejecución.
    total_urls: int

    # Guarda los resultados por URL.
    resultados: List[ResultadoUrl]

    # Guarda el nombre del cliente inferido o definido.
    cliente: str

    # Guarda la fecha real de ejecución en formato ISO.
    fecha_ejecucion: str

    # Guarda el gestor responsable del informe.
    gestor: str

    # Guarda las fuentes realmente activas en la ejecución.
    fuentes_activas: List[str] = field(default_factory=lambda: ["sitemap", "rastreo_tecnico", "html"])

    # Guarda fuentes que se intentaron usar pero fallaron en ejecución.
    fuentes_fallidas: List[str] = field(default_factory=list)

    # Guarda los resultados de rendimiento obtenidos desde PageSpeed.
    rendimiento: List[ResultadoRendimiento] = field(default_factory=list)

    # Guarda estado por URL y estrategia cuando PageSpeed falla o devuelve datos parciales.
    pagespeed_estado: dict[str, dict[str, str]] = field(default_factory=dict)

    # Guarda el informe narrativo opcional generado por IA.
    resumen_ia: Optional[str] = None
