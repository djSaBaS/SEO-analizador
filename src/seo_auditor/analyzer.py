# Importa el analizador HTML para tipado explícito.
from bs4 import BeautifulSoup

# Importa tipos del dominio del proyecto.
from seo_auditor.models import HallazgoSeo, ResultadoAuditoria, ResultadoUrl

# Importa funciones de obtención de HTML.
from seo_auditor.fetcher import obtener_metadatos_html

# Importa utilidades para clasificación interna.
from seo_auditor.utils import inferir_tipo_url


# Añade un hallazgo de forma declarativa y uniforme.
def crear_hallazgo(tipo: str, severidad: str, descripcion: str, recomendacion: str) -> HallazgoSeo:
    """
    Crea una instancia de hallazgo SEO.

    Parameters
    ----------
    tipo : str
        Categoría del hallazgo.
    severidad : str
        Severidad del hallazgo.
    descripcion : str
        Descripción del problema.
    recomendacion : str
        Acción recomendada.

    Returns
    -------
    HallazgoSeo
        Hallazgo construido de forma uniforme.
    """

    # Devuelve un objeto normalizado del dominio.
    return HallazgoSeo(tipo=tipo, severidad=severidad, descripcion=descripcion, recomendacion=recomendacion)


# Extrae un valor meta concreto desde el HTML.
def extraer_meta(html: BeautifulSoup, nombre: str) -> str:
    """
    Obtiene el contenido de una meta etiqueta por atributo `name`.

    Parameters
    ----------
    html : BeautifulSoup
        Documento HTML parseado.
    nombre : str
        Valor del atributo `name` a buscar.

    Returns
    -------
    str
        Contenido de la meta si existe o cadena vacía.
    """

    # Busca la meta etiqueta por nombre exacto.
    etiqueta = html.find("meta", attrs={"name": nombre})

    # Devuelve el contenido si la etiqueta existe y contiene el atributo esperado.
    return etiqueta.get("content", "").strip() if etiqueta else ""


# Analiza una sola URL y genera un resultado técnico.
def auditar_url(url: str, timeout: int) -> ResultadoUrl:
    """
    Analiza una URL y devuelve su resultado técnico SEO básico.

    Parameters
    ----------
    url : str
        URL a analizar.
    timeout : int
        Tiempo máximo de espera HTTP.

    Returns
    -------
    ResultadoUrl
        Resultado estructurado del análisis.
    """

    # Intenta descargar y analizar la URL con control explícito de errores.
    try:
        # Descarga la respuesta HTTP y el documento HTML parseado.
        respuesta, html = obtener_metadatos_html(url, timeout)

        # Extrae el título si existe dentro del documento.
        title = html.title.get_text(strip=True) if html.title else ""

        # Busca el primer H1 útil del documento.
        h1_tag = html.find("h1")

        # Extrae el texto del H1 si se ha localizado.
        h1 = h1_tag.get_text(strip=True) if h1_tag else ""

        # Extrae la meta descripción para evaluar completitud on-page.
        meta_description = extraer_meta(html, "description")

        # Busca un enlace canonical dentro del head.
        canonical_tag = html.find("link", rel="canonical")

        # Obtiene el href de la canonical cuando exista.
        canonical = canonical_tag.get("href", "").strip() if canonical_tag else None

        # Lee la meta robots para buscar instrucciones noindex.
        robots = extraer_meta(html, "robots").lower()

        # Determina si la página está marcada como noindex.
        noindex = "noindex" in robots

        # Inicializa la colección de hallazgos detectados.
        hallazgos = []

        # Añade hallazgo si la página redirige.
        if len(respuesta.history) > 0:
            # Registra un problema de redirección para priorizar limpieza.
            hallazgos.append(
                crear_hallazgo(
                    tipo="indexación",
                    severidad="alta",
                    descripcion="La URL devuelve una redirección y no debería indexarse tal cual.",
                    recomendacion="Revisar enlaces internos, sitemap y canonicals para apuntar siempre a la URL final.",
                )
            )

        # Añade hallazgo si el title está vacío.
        if not title:
            # Señala una carencia básica de SEO on-page.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
                    severidad="alta",
                    descripcion="La página no tiene etiqueta title visible.",
                    recomendacion="Definir un title único, descriptivo y alineado con la intención de búsqueda.",
                )
            )

        # Añade hallazgo si el H1 está vacío.
        if not h1:
            # Señala una carencia estructural importante.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
                    severidad="media",
                    descripcion="La página no tiene encabezado H1.",
                    recomendacion="Añadir un H1 único que resuma el propósito principal de la página.",
                )
            )

        # Añade hallazgo si la meta descripción está vacía.
        if not meta_description:
            # Señala una oportunidad clara de mejora en snippets.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
                    severidad="media",
                    descripcion="La página no tiene meta description.",
                    recomendacion="Añadir una meta description persuasiva y única para mejorar el CTR.",
                )
            )

        # Añade hallazgo si falta la canonical.
        if not canonical:
            # Señala una oportunidad de consolidación de señales SEO.
            hallazgos.append(
                crear_hallazgo(
                    tipo="técnico",
                    severidad="media",
                    descripcion="La página no declara canonical.",
                    recomendacion="Definir canonical autorreferente o consolidada según la estrategia de indexación.",
                )
            )

        # Añade hallazgo si la página está marcada como noindex.
        if noindex:
            # Informa de una directiva crítica de indexación.
            hallazgos.append(
                crear_hallazgo(
                    tipo="indexación",
                    severidad="alta",
                    descripcion="La página está marcada como noindex.",
                    recomendacion="Confirmar si debe excluirse del índice o retirar la directiva si la página es estratégica.",
                )
            )

        # Devuelve el resultado consolidado de la URL.
        return ResultadoUrl(
            # Guarda la URL original auditada.
            url=url,
            # Infiere el tipo lógico de recurso.
            tipo=inferir_tipo_url(url),
            # Guarda el código HTTP final observado.
            estado_http=respuesta.status_code,
            # Indica si hubo redirección.
            redirecciona=len(respuesta.history) > 0,
            # Guarda la URL final resuelta por HTTP.
            url_final=str(respuesta.url),
            # Guarda el title extraído del documento.
            title=title,
            # Guarda el H1 principal extraído.
            h1=h1,
            # Guarda la meta description extraída.
            meta_description=meta_description,
            # Guarda la canonical detectada o None.
            canonical=canonical,
            # Guarda si existe directiva noindex.
            noindex=noindex,
            # Guarda todos los hallazgos acumulados.
            hallazgos=hallazgos,
        )

    # Captura cualquier error controlado sin exponer trazas sensibles al usuario final.
    except Exception as exc:
        # Devuelve un resultado seguro y trazable para la URL fallida.
        return ResultadoUrl(
            # Conserva la URL original para diagnóstico.
            url=url,
            # Infiere el tipo para no perder contexto.
            tipo=inferir_tipo_url(url),
            # Usa cero como marcador cuando no se obtuvo respuesta útil.
            estado_http=0,
            # Indica que no se puede confirmar redirección por error.
            redirecciona=False,
            # Conserva la URL original como referencia final.
            url_final=url,
            # Devuelve campos textuales vacíos al no disponer de HTML válido.
            title="",
            # Devuelve H1 vacío por ausencia de análisis HTML.
            h1="",
            # Devuelve meta description vacía por ausencia de análisis HTML.
            meta_description="",
            # Devuelve canonical desconocida.
            canonical=None,
            # Marca noindex como falso por falta de evidencia.
            noindex=False,
            # Registra un hallazgo de error técnico accionable.
            hallazgos=[
                crear_hallazgo(
                    tipo="técnico",
                    severidad="alta",
                    descripcion="No se pudo analizar la URL por un error de descarga o parseo.",
                    recomendacion="Revisar disponibilidad, certificados, bloqueos WAF o errores del servidor.",
                )
            ],
            # Guarda un mensaje controlado y sin secretos del error.
            error=str(exc),
        )


# Construye el resultado global a partir de una colección de URLs.
def auditar_urls(sitemap: str, urls: list[str], timeout: int) -> ResultadoAuditoria:
    """
    Ejecuta la auditoría SEO básica de varias URLs.

    Parameters
    ----------
    sitemap : str
        Sitemap origen de la ejecución.
    urls : list[str]
        URLs a auditar.
    timeout : int
        Tiempo máximo por petición HTTP.

    Returns
    -------
    ResultadoAuditoria
        Resultado global de la ejecución.
    """

    # Analiza cada URL de forma secuencial para una primera versión simple y estable.
    resultados = [auditar_url(url, timeout) for url in urls]

    # Devuelve el agregado final de la auditoría.
    return ResultadoAuditoria(sitemap=sitemap, total_urls=len(resultados), resultados=resultados)
