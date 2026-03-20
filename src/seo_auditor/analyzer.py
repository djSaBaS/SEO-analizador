# Importa el analizador HTML para tipado explícito.
from bs4 import BeautifulSoup

# Importa funciones de obtención de HTML.
from seo_auditor.fetcher import obtener_metadatos_html

# Importa tipos del dominio del proyecto.
from seo_auditor.models import HallazgoSeo, ResultadoAuditoria, ResultadoUrl

# Importa utilidades para clasificación interna y progreso.
from seo_auditor.utils import inferir_tipo_url, iterar_con_progreso


# Crea una matriz de clasificación SEO transparente y extensible.
def clasificar_hallazgo(tipo: str, descripcion: str) -> dict[str, str]:
    """
    Clasifica un hallazgo con severidad, área, impacto, esfuerzo y prioridad.
    """

    # Convierte la descripción a minúsculas para aplicar reglas homogéneas.
    descripcion_normalizada = descripcion.lower()

    # Define reglas ordenadas desde casos más críticos a menos críticos.
    reglas = [
        ("5xx", {"severidad": "crítica", "area": "Infraestructura", "impacto": "Muy alto", "esfuerzo": "Medio", "prioridad": "P1"}),
        ("4xx", {"severidad": "alta", "area": "Indexación", "impacto": "Alto", "esfuerzo": "Bajo", "prioridad": "P1"}),
        ("redirección", {"severidad": "alta", "area": "Arquitectura", "impacto": "Alto", "esfuerzo": "Bajo", "prioridad": "P1"}),
        ("canonical incoherente", {"severidad": "alta", "area": "Indexación", "impacto": "Alto", "esfuerzo": "Medio", "prioridad": "P1"}),
        ("noindex", {"severidad": "alta", "area": "Indexación", "impacto": "Alto", "esfuerzo": "Bajo", "prioridad": "P1"}),
        ("title", {"severidad": "alta", "area": "Contenido", "impacto": "Alto", "esfuerzo": "Bajo", "prioridad": "P2"}),
        ("meta description", {"severidad": "media", "area": "Contenido", "impacto": "Medio", "esfuerzo": "Bajo", "prioridad": "P2"}),
        ("h1", {"severidad": "media", "area": "Contenido", "impacto": "Medio", "esfuerzo": "Bajo", "prioridad": "P2"}),
        ("canonical", {"severidad": "media", "area": "Indexación", "impacto": "Medio", "esfuerzo": "Bajo", "prioridad": "P2"}),
        ("menor", {"severidad": "baja", "area": "Calidad", "impacto": "Bajo", "esfuerzo": "Bajo", "prioridad": "P3"}),
    ]

    # Recorre las reglas en orden para localizar la primera coincidencia.
    for patron, clasificacion in reglas:
        # Aplica coincidencia por inclusión simple para facilidad de mantenimiento.
        if patron in descripcion_normalizada:
            # Devuelve la clasificación asociada al patrón encontrado.
            return clasificacion

    # Devuelve una clasificación informativa por defecto cuando no hay coincidencias.
    return {"severidad": "informativa", "area": tipo.title(), "impacto": "Bajo", "esfuerzo": "Bajo", "prioridad": "P4"}


# Añade un hallazgo de forma declarativa y uniforme.
def crear_hallazgo(tipo: str, descripcion: str, recomendacion: str) -> HallazgoSeo:
    """
    Crea una instancia de hallazgo SEO aplicando clasificación automática.
    """

    # Calcula la clasificación basada en reglas mantenibles.
    clasificacion = clasificar_hallazgo(tipo, descripcion)

    # Devuelve un objeto normalizado del dominio.
    return HallazgoSeo(
        tipo=tipo,
        severidad=clasificacion["severidad"],
        descripcion=descripcion,
        recomendacion=recomendacion,
        area=clasificacion["area"],
        impacto=clasificacion["impacto"],
        esfuerzo=clasificacion["esfuerzo"],
        prioridad=clasificacion["prioridad"],
    )


# Extrae un valor meta concreto desde el HTML.
def extraer_meta(html: BeautifulSoup, nombre: str) -> str:
    """
    Obtiene el contenido de una meta etiqueta por atributo `name`.
    """

    # Busca la meta etiqueta por nombre exacto.
    etiqueta = html.find("meta", attrs={"name": nombre})

    # Devuelve el contenido si la etiqueta existe y contiene el atributo esperado.
    return etiqueta.get("content", "").strip() if etiqueta else ""


# Analiza una sola URL y genera un resultado técnico.
def auditar_url(url: str, timeout: int) -> ResultadoUrl:
    """
    Analiza una URL y devuelve su resultado técnico SEO básico.
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

        # Registra código 5xx como incidencia crítica.
        if respuesta.status_code >= 500:
            # Añade un hallazgo de servidor no disponible.
            hallazgos.append(
                crear_hallazgo(
                    tipo="técnico",
                    descripcion="La URL devuelve un error 5xx y no es accesible para rastreo.",
                    recomendacion="Corregir el error de servidor con prioridad inmediata.",
                )
            )

        # Registra código 4xx como incidencia alta.
        if 400 <= respuesta.status_code < 500:
            # Añade un hallazgo de recurso no accesible.
            hallazgos.append(
                crear_hallazgo(
                    tipo="indexación",
                    descripcion="La URL devuelve un error 4xx y aparece en activos auditados.",
                    recomendacion="Eliminar la URL del sitemap o restaurar una respuesta 200 estable.",
                )
            )

        # Añade hallazgo si la página redirige.
        if len(respuesta.history) > 0:
            # Registra un problema de redirección para priorizar limpieza.
            hallazgos.append(
                crear_hallazgo(
                    tipo="indexación",
                    descripcion="La URL devuelve una redirección y debería apuntar directamente al destino final.",
                    recomendacion="Revisar enlaces internos, sitemap y canonicals para apuntar a la URL final.",
                )
            )

        # Añade hallazgo si el title está vacío.
        if not title:
            # Señala una carencia básica de SEO on-page.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
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
                    descripcion="La página no declara canonical.",
                    recomendacion="Definir canonical autorreferente o consolidada según la estrategia de indexación.",
                )
            )

        # Añade hallazgo si canonical apunta a otra URL distinta no prevista.
        if canonical and canonical != url and canonical != str(respuesta.url):
            # Añade una alerta de canonical potencialmente incoherente.
            hallazgos.append(
                crear_hallazgo(
                    tipo="indexación",
                    descripcion="Canonical incoherente detectada respecto a la URL final auditada.",
                    recomendacion="Alinear canonical con la URL indexable preferida y revisar consistencia interna.",
                )
            )

        # Añade hallazgo si la página está marcada como noindex.
        if noindex:
            # Informa de una directiva crítica de indexación.
            hallazgos.append(
                crear_hallazgo(
                    tipo="indexación",
                    descripcion="La página está marcada como noindex.",
                    recomendacion="Confirmar si debe excluirse del índice o retirar la directiva si es estratégica.",
                )
            )

        # Devuelve el resultado consolidado de la URL.
        return ResultadoUrl(
            url=url,
            tipo=inferir_tipo_url(url),
            estado_http=respuesta.status_code,
            redirecciona=len(respuesta.history) > 0,
            url_final=str(respuesta.url),
            title=title,
            h1=h1,
            meta_description=meta_description,
            canonical=canonical,
            noindex=noindex,
            hallazgos=hallazgos,
        )

    # Captura cualquier error controlado sin exponer trazas sensibles al usuario final.
    except Exception as exc:
        # Devuelve un resultado seguro y trazable para la URL fallida.
        return ResultadoUrl(
            url=url,
            tipo=inferir_tipo_url(url),
            estado_http=0,
            redirecciona=False,
            url_final=url,
            title="",
            h1="",
            meta_description="",
            canonical=None,
            noindex=False,
            hallazgos=[
                crear_hallazgo(
                    tipo="técnico",
                    descripcion="No se pudo analizar la URL por un error de descarga o parseo.",
                    recomendacion="Revisar disponibilidad, certificados, bloqueos WAF o errores del servidor.",
                )
            ],
            error=str(exc),
        )


# Construye el resultado global a partir de una colección de URLs.
def auditar_urls(sitemap: str, urls: list[str], timeout: int, cliente: str, fecha_ejecucion: str, gestor: str) -> ResultadoAuditoria:
    """
    Ejecuta la auditoría SEO básica de varias URLs.
    """

    # Inicializa la colección de resultados de URLs auditadas.
    resultados: list[ResultadoUrl] = []

    # Recorre URLs con barra de progreso visible en consola.
    for url in iterar_con_progreso(urls, "Auditoría técnica", "URL"):
        # Ejecuta auditoría de la URL actual.
        resultados.append(auditar_url(url, timeout))

    # Devuelve el agregado final de la auditoría.
    return ResultadoAuditoria(
        sitemap=sitemap,
        total_urls=len(resultados),
        resultados=resultados,
        cliente=cliente,
        fecha_ejecucion=fecha_ejecucion,
        gestor=gestor,
    )
