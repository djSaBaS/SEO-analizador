# Importa utilidades para crear modelos de datos simples y seguros.
from dataclasses import dataclass, field

# Importa tipos estándar para mejorar legibilidad y validación estática.
from typing import Any, List, Optional


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


# Define métrica agregada de Google Analytics 4 por página.
@dataclass(slots=True)
class MetricaAnalyticsPagina:
    """
    Representa una fila agregada de comportamiento de usuario por URL.
    """

    # Guarda ruta o landing principal de la página.
    url: str

    # Guarda sesiones agregadas en el rango.
    sesiones: float

    # Guarda usuarios agregados en el rango.
    usuarios: float

    # Guarda tasa de rebote agregada en formato decimal.
    rebote: float

    # Guarda duración media de sesión en segundos.
    duracion_media: float

    # Guarda conversiones agregadas cuando existan.
    conversiones: float

    # Guarda evaluación cualitativa de calidad de tráfico.
    calidad_trafico: str = "media"


# Define resumen agregado de Google Analytics 4.
@dataclass(slots=True)
class ResumenAnalytics:
    """
    Resume métricas globales de comportamiento para la propiedad GA4.
    """

    # Guarda total de sesiones en el rango.
    sesiones_totales: float = 0.0

    # Guarda total de usuarios en el rango.
    usuarios_totales: float = 0.0

    # Guarda rebote promedio ponderado por sesiones.
    rebote_medio: float = 0.0

    # Guarda duración media ponderada por sesiones.
    duracion_media: float = 0.0

    # Guarda conversiones totales.
    conversiones: float = 0.0


# Define bloque completo de datos Analytics opcionales.
@dataclass(slots=True)
class DatosAnalytics:
    """
    Contiene datos autenticados opcionales de Google Analytics 4.
    """

    # Indica si la extracción de GA4 fue efectiva.
    activo: bool

    # Guarda mensaje de error controlado cuando exista.
    error: Optional[str] = None

    # Guarda property id consultado.
    property_id: str = ""

    # Guarda fecha inicial efectiva de consulta.
    date_from: str = ""

    # Guarda fecha final efectiva de consulta.
    date_to: str = ""

    # Guarda métricas por página.
    paginas: List[MetricaAnalyticsPagina] = field(default_factory=list)

    # Guarda resumen agregado del periodo.
    resumen: ResumenAnalytics = field(default_factory=ResumenAnalytics)

    # Guarda hallazgos de cruce GA4 + GSC cuando aplique.
    cruces_gsc: List[dict[str, object]] = field(default_factory=list)


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

    # Guarda datos opcionales autenticados de Google Analytics 4.
    analytics: DatosAnalytics = field(default_factory=lambda: DatosAnalytics(activo=False, error="Analytics no configurado"))

    # Guarda el informe narrativo opcional generado por IA.
    resumen_ia: Optional[str] = None

    # Guarda fecha inicial global del periodo analizado.
    periodo_date_from: str = ""

    # Guarda fecha final global del periodo analizado.
    periodo_date_to: str = ""


# Define los flags de integraciones habilitadas para una ejecución.
@dataclass(slots=True)
class FlagsIntegracionesAuditoria:
    """
    Centraliza qué integraciones externas participan en la auditoría.
    """

    # Indica si Search Console está habilitado en la ejecución.
    usar_search_console: bool = False

    # Indica si Google Analytics 4 está habilitado en la ejecución.
    usar_analytics: bool = False

    # Indica si PageSpeed está habilitado en la ejecución.
    usar_pagespeed: bool = False

    # Indica si la generación de resumen con IA está habilitada.
    usar_ia: bool = False

    # Indica si se debe generar el informe GA4 Premium.
    usar_ga4_premium: bool = False


# Define la configuración de caché para integraciones costosas.
@dataclass(slots=True)
class ConfiguracionCacheAuditoria:
    """
    Representa la estrategia de caché usada durante la ejecución.
    """

    # Guarda la ruta base de caché local.
    ruta_cache: str = ""

    # Guarda el TTL de caché en segundos.
    ttl_segundos: int = 0

    # Indica si se invalida la caché antes de ejecutar.
    invalidar_antes_de_ejecutar: bool = False


# Define las opciones documentales y de formato de entregables.
@dataclass(slots=True)
class ConfiguracionInforme:
    """
    Agrupa preferencias de generación documental del informe.
    """

    # Guarda el perfil de generación activo.
    perfil_generacion: str = "auditoria-seo-completa"

    # Guarda el modo operativo del CLI para contexto documental.
    modo: str = "completo"

    # Guarda la ruta base donde se exportarán entregables.
    carpeta_salida: str = "./salidas"

    # Lista de entregables solicitados por el perfil.
    entregables_solicitados: List[str] = field(default_factory=list)


# Define el contrato normalizado de entrada de una auditoría.
@dataclass(slots=True)
class AuditoriaRequest:
    """
    Modelo de entrada para coordinar auditoría e integraciones sin argumentos sueltos.
    """

    # Guarda el sitemap objetivo de análisis.
    sitemap: str

    # Guarda fecha inicial efectiva del periodo analizado.
    periodo_desde: str

    # Guarda fecha final efectiva del periodo analizado.
    periodo_hasta: str

    # Guarda nombre del gestor responsable del informe.
    gestor: str

    # Guarda nombre del cliente cuando venga definido por CLI.
    cliente: str = ""

    # Guarda el modelo IA a usar para generación narrativa.
    modelo_ia: str = ""

    # Guarda si se aplica un muestreo rápido de URLs.
    modo_rapido: bool = False

    # Guarda máximo de muestras que se enviarán al motor IA.
    max_muestras_ia: int = 15

    # Guarda URL única de PageSpeed cuando aplique.
    pagepsi_url: str = ""

    # Guarda ruta de archivo de URLs para PageSpeed cuando aplique.
    pagepsi_list_path: str = ""

    # Guarda límite máximo de URLs en flujo PageSpeed.
    max_pagepsi_urls: int = 0

    # Guarda timeout para llamadas PageSpeed.
    pagepsi_timeout: int = 0

    # Guarda reintentos para llamadas PageSpeed.
    pagepsi_reintentos: int = -1

    # Guarda flags de integración activos para la ejecución.
    integraciones: FlagsIntegracionesAuditoria = field(default_factory=FlagsIntegracionesAuditoria)

    # Guarda configuración de caché aplicada.
    cache: ConfiguracionCacheAuditoria = field(default_factory=ConfiguracionCacheAuditoria)

    # Guarda opciones documentales del informe.
    informe: ConfiguracionInforme = field(default_factory=ConfiguracionInforme)

    # Guarda configuración global legado para adaptadores existentes.
    configuracion: Any = None

    # Guarda argumentos legado para mantener compatibilidad gradual.
    argumentos: Any = None


# Define el resumen de artefactos documentales producidos por la auditoría.
@dataclass(slots=True)
class ResultadoEntregables:
    """
    Resume archivos generados, omitidos y errores no fatales de exportación.
    """

    # Lista de identificadores de entregables exportados.
    generados: List[str] = field(default_factory=list)

    # Lista de entregables omitidos con motivo.
    omitidos: List[str] = field(default_factory=list)

    # Lista de errores no fatales detectados en exportación.
    errores_no_fatales: List[str] = field(default_factory=list)


# Define un resumen ejecutivo de la ejecución para trazabilidad operativa.
@dataclass(slots=True)
class ResumenEjecucion:
    """
    Consolida estado operativo de la corrida de auditoría.
    """

    # Indica código de retorno final del proceso.
    codigo_salida: int = 0

    # Guarda total de URLs incluidas en el análisis.
    total_urls_analizadas: int = 0

    # Guarda fuentes activas efectivas en la ejecución.
    fuentes_activas: List[str] = field(default_factory=list)

    # Guarda fuentes que fallaron durante la ejecución.
    fuentes_fallidas: List[str] = field(default_factory=list)

    # Indica si se aplicó invalidación de caché.
    cache_invalidada: bool = False


# Define el contrato estable de salida entre servicios de dominio.
@dataclass(slots=True)
class AuditoriaResult:
    """
    Encapsula el resultado completo de auditoría para intercambio entre servicios.
    """

    # Guarda el detalle técnico consolidado de la auditoría.
    auditoria: ResultadoAuditoria

    # Guarda el resumen de entregables documentales.
    entregables: ResultadoEntregables = field(default_factory=ResultadoEntregables)

    # Guarda el resumen operativo de ejecución.
    resumen_ejecucion: ResumenEjecucion = field(default_factory=ResumenEjecucion)
