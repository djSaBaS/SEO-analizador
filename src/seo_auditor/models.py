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

    # Guarda el número total de palabras del contenido extraído.
    palabras: int = 0

    # Guarda la densidad de texto limpio frente al total de texto bruto.
    densidad_texto: float = 0.0

    # Guarda la longitud media por palabra detectada.
    longitud_media_palabra: float = 0.0

    # Guarda el ratio de tamaño entre texto extraído y HTML completo.
    ratio_texto_html: float = 0.0

    # Guarda una etiqueta cualitativa de calidad de contenido.
    calidad_contenido: str = "baja"

    # Indica si la URL cae en umbral de thin content.
    thin_content: bool = False

    # Guarda el texto limpio extraído para análisis posterior.
    texto_extraido: str = ""

    # Guarda hash estable del contenido para detectar duplicidad aproximada.
    hash_contenido: str = ""

    # Indica si existe un único H1 en la URL.
    h1_unico: bool = False

    # Indica si la jerarquía de headings es coherente.
    estructura_headings_correcta: bool = True

    # Guarda el total de imágenes sin atributo ALT.
    imagenes_sin_alt: int = 0

    # Guarda el peso estimado de imágenes en kilobytes.
    peso_imagenes_estimado_kb: float = 0.0

    # Indica si se detecta lazy-load en imágenes.
    lazy_load_detectado: bool = False

    # Guarda un error controlado si la auditoría de la URL falló.
    error: Optional[str] = None


# Define métrica agregada de Search Console por página.
@dataclass(slots=True)
class MetricaGscPagina:
    """
    Representa una fila agregada de rendimiento orgánico por URL.
    """

    # Guarda URL canónica de la propiedad.
    url: str

    # Guarda clics orgánicos agregados.
    clicks: float

    # Guarda impresiones orgánicas agregadas.
    impresiones: float

    # Guarda CTR agregado en formato decimal.
    ctr: float

    # Guarda posición media agregada.
    posicion_media: float

    # Guarda dispositivo cuando aplique desglose.
    dispositivo: str = ""

    # Guarda país cuando aplique desglose.
    pais: str = ""


# Define métrica agregada de Search Console por query.
@dataclass(slots=True)
class MetricaGscQuery:
    """
    Representa una fila agregada de rendimiento orgánico por consulta.
    """

    # Guarda texto de la consulta.
    query: str

    # Guarda clics orgánicos agregados.
    clicks: float

    # Guarda impresiones orgánicas agregadas.
    impresiones: float

    # Guarda CTR agregado en formato decimal.
    ctr: float

    # Guarda posición media agregada.
    posicion_media: float

    # Guarda URL asociada principal cuando exista cruce.
    url_asociada: str = ""


# Define bloque completo de datos Search Console opcionales.
@dataclass(slots=True)
class DatosSearchConsole:
    """
    Contiene datos autenticados opcionales de Google Search Console.
    """

    # Indica si la extracción GSC fue efectiva.
    activo: bool

    # Guarda mensaje de error controlado cuando exista.
    error: Optional[str] = None

    # Guarda propiedad siteUrl consultada.
    site_url: str = ""

    # Guarda fecha inicial efectiva de consulta.
    date_from: str = ""

    # Guarda fecha final efectiva de consulta.
    date_to: str = ""

    # Guarda métricas por página.
    paginas: List[MetricaGscPagina] = field(default_factory=list)

    # Guarda métricas por query.
    queries: List[MetricaGscQuery] = field(default_factory=list)

    # Guarda cruce crudo query+page para mapping inicial.
    filas_query_pagina: List[dict[str, object]] = field(default_factory=list)

    # Guarda desglose opcional por dispositivo.
    filas_dispositivo: List[dict[str, object]] = field(default_factory=list)

    # Guarda desglose opcional por país.
    filas_pais: List[dict[str, object]] = field(default_factory=list)


# Define una recomendación operativa de gestión de indexación por URL.
@dataclass(slots=True)
class DecisionIndexacion:
    """
    Representa una decisión accionable de indexación para una URL concreta.
    """

    # Guarda la URL evaluada por el motor de indexación inteligente.
    url: str

    # Guarda clasificación final de indexación.
    clasificacion: str

    # Guarda el motivo principal de la clasificación.
    motivo: str

    # Guarda la acción recomendada de ejecución.
    accion_recomendada: str

    # Guarda prioridad sugerida para el equipo.
    prioridad: str


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

    # Guarda resumen de indexación y rastreo (robots/sitemap).
    indexacion_rastreo: dict[str, object] = field(default_factory=dict)

    # Guarda decisiones de gestión de indexación inteligente por URL.
    gestion_indexacion: List[DecisionIndexacion] = field(default_factory=list)

    # Guarda score técnico agregado en escala 0-100.
    score_tecnico: Optional[float] = None

    # Guarda score de contenido agregado en escala 0-100.
    score_contenido: Optional[float] = None

    # Guarda score de rendimiento agregado en escala 0-100.
    score_rendimiento: Optional[float] = None

    # Guarda SEO score global agregado en escala 0-100.
    seo_score_global: Optional[float] = None

    # Guarda datos opcionales autenticados de Search Console.
    search_console: DatosSearchConsole = field(default_factory=lambda: DatosSearchConsole(activo=False, error="No configurado"))

    # Guarda el informe narrativo opcional generado por IA.
    resumen_ia: Optional[str] = None
