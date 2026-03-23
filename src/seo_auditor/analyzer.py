# Importa el analizador HTML para tipado explícito.
from bs4 import BeautifulSoup

# Importa utilidades estándar para normalización robusta de URL.
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

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
        ("slash final", {"severidad": "baja", "area": "Arquitectura", "impacto": "Bajo", "esfuerzo": "Bajo", "prioridad": "P3"}),
        ("canonical realmente incoherente", {"severidad": "alta", "area": "Indexación", "impacto": "Alto", "esfuerzo": "Medio", "prioridad": "P1"}),
        ("canonical potencialmente incoherente", {"severidad": "media", "area": "Indexación", "impacto": "Medio", "esfuerzo": "Medio", "prioridad": "P2"}),
        ("canonical con diferencia menor normalizable", {"severidad": "baja", "area": "Indexación", "impacto": "Bajo", "esfuerzo": "Bajo", "prioridad": "P3"}),
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


# Determina si una redirección es solo normalización de slash final.
def _es_redireccion_solo_slash(url_origen: str, url_destino: str) -> bool:
    """
    Evalúa si el cambio entre origen y destino es únicamente barra final.
    """

    # Limpia barra final para comparar rutas equivalentes.
    origen_limpio = url_origen.rstrip("/")

    # Limpia barra final de la URL de destino.
    destino_limpio = url_destino.rstrip("/")

    # Compara ambos valores para detectar normalización trivial.
    return origen_limpio == destino_limpio


# Normaliza una URL para comparaciones SEO robustas y consistentes.
def _normalizar_url_comparable(url: str) -> str:
    """
    Normaliza esquema, host, puertos, barra final, query y fragmento para comparar URLs.
    """

    # Parsea la URL de entrada para manipular sus componentes.
    parseada = urlparse(url.strip())

    # Normaliza esquema en minúsculas.
    esquema = parseada.scheme.lower()

    # Normaliza hostname en minúsculas.
    host = (parseada.hostname or "").lower()

    # Lee el puerto explícito cuando exista con tolerancia a valores inválidos.
    try:
        # Obtiene puerto parseado de forma segura.
        puerto = parseada.port
    except ValueError:
        # Ignora puerto inválido para no romper la auditoría completa.
        puerto = None

    # Descarta puertos por defecto para evitar falsos positivos.
    if (esquema == "http" and puerto == 80) or (esquema == "https" and puerto == 443):
        # Limpia puerto redundante.
        puerto = None

    # Construye netloc final con puerto solo cuando sea necesario.
    netloc = f"{host}:{puerto}" if puerto else host

    # Limpia ruta vacía para dejar siempre barra raíz.
    ruta = parseada.path or "/"

    # Elimina barra final solo cuando no sea la raíz del dominio.
    if ruta != "/" and ruta.endswith("/"):
        # Recorta slash final para evitar falsos positivos triviales.
        ruta = ruta.rstrip("/")

    # Ordena query params para comparación estable.
    query_ordenada = urlencode(sorted(parse_qsl(parseada.query, keep_blank_values=True)))

    # Reconstruye URL sin fragmento para comparación técnica.
    return urlunparse((esquema, netloc, ruta, "", query_ordenada, ""))


# Clasifica coherencia de canonical considerando normalizaciones SEO comunes.
def _clasificar_canonical(url_auditada: str, url_final: str, canonical: str, estado_http: int) -> str:
    """
    Devuelve `coherente`, `menor`, `potencial` o `incoherente` según el nivel de desviación detectado.
    """

    # Normaliza la URL auditada para comparación homogénea.
    auditada_normalizada = _normalizar_url_comparable(url_auditada)

    # Normaliza la URL final servida.
    final_normalizada = _normalizar_url_comparable(url_final)

    # Normaliza canonical declarada en el HTML.
    canonical_normalizada = _normalizar_url_comparable(canonical)

    # Detecta canonical autorreferente contra URL auditada o final.
    if canonical_normalizada in {auditada_normalizada, final_normalizada}:
        # Clasifica como coherente para evitar falsos positivos.
        return "coherente"

    # Evalúa si la diferencia es solo slash final entre canonical y URL de referencia.
    if canonical_normalizada.rstrip("/") in {auditada_normalizada.rstrip("/"), final_normalizada.rstrip("/")}:
        # Clasifica como diferencia menor para evitar falsos positivos.
        return "menor" if estado_http == 200 else "potencial"

    # Evalúa cambio de host/ruta como potencial incoherencia.
    return "incoherente"


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
        h1_tags = html.find_all("h1")

        # Extrae el texto del H1 si se ha localizado.
        h1 = h1_tags[0].get_text(strip=True) if h1_tags else ""

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
            # Detecta si la redirección es solo por slash final.
            if _es_redireccion_solo_slash(url, str(respuesta.url)):
                # Registra incidencia leve para evitar sobredimensionar el informe.
                hallazgos.append(
                    crear_hallazgo(
                        tipo="indexación",
                        descripcion="La URL redirecciona solo para normalizar slash final.",
                        recomendacion="Unificar enlazado interno y sitemap con la versión final para reducir saltos innecesarios.",
                    )
                )
            else:
                # Registra un problema de redirección relevante.
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
        # Añade hallazgo si el title es demasiado corto.
        elif len(title) < 15:
            # Señala posible falta de contexto semántico en SERP.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
                    descripcion="Title demasiado corto para competir con contexto semántico.",
                    recomendacion="Ampliar title a un rango orientativo de 15-60 caracteres con intención clara.",
                )
            )
        # Añade hallazgo si el title es demasiado largo.
        elif len(title) > 60:
            # Señala riesgo de truncado en snippets.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
                    descripcion="Title demasiado largo y con riesgo de truncado en resultados.",
                    recomendacion="Reducir title a un rango orientativo de 15-60 caracteres priorizando keyword principal.",
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
        # Añade hallazgo cuando se detectan múltiples H1 en una misma URL.
        elif len(h1_tags) > 1:
            # Señala potencial conflicto jerárquico de encabezados.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
                    descripcion="Se detectaron múltiples H1 en la misma página.",
                    recomendacion="Mantener un único H1 principal y usar H2/H3 para la jerarquía restante.",
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
        # Añade hallazgo si la meta description es demasiado corta.
        elif len(meta_description) < 70:
            # Señala oportunidad de mejorar relevancia y CTR.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
                    descripcion="Meta description demasiado corta para comunicar valor.",
                    recomendacion="Ajustar meta description a un rango orientativo de 70-160 caracteres.",
                )
            )
        # Añade hallazgo si la meta description es demasiado larga.
        elif len(meta_description) > 160:
            # Señala riesgo de truncado y pérdida de mensaje.
            hallazgos.append(
                crear_hallazgo(
                    tipo="contenido",
                    descripcion="Meta description demasiado larga y con riesgo de truncado.",
                    recomendacion="Reducir meta description a un rango orientativo de 70-160 caracteres.",
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

        # Evalúa coherencia de canonical con normalización robusta cuando exista.
        if canonical:
            # Clasifica el nivel real de desviación detectada.
            estado_canonical = _clasificar_canonical(url, str(respuesta.url), canonical, respuesta.status_code)

            # Registra diferencia menor para trazabilidad sin alarmismo.
            if estado_canonical == "menor":
                # Añade hallazgo de baja severidad no bloqueante.
                hallazgos.append(
                    crear_hallazgo(
                        tipo="indexación",
                        descripcion="Canonical con diferencia menor normalizable respecto a URL auditada/final.",
                        recomendacion="Unificar formato de canonical (slash final, host y esquema) para consistencia técnica.",
                    )
                )

            # Registra posible incoherencia cuando hay señales mixtas.
            if estado_canonical == "potencial":
                # Añade alerta moderada para revisión manual.
                hallazgos.append(
                    crear_hallazgo(
                        tipo="indexación",
                        descripcion="Canonical potencialmente incoherente por diferencia no crítica de normalización.",
                        recomendacion="Revisar canonical y redirecciones para confirmar la URL indexable preferida.",
                    )
                )

            # Registra incoherencia real para actuación prioritaria.
            if estado_canonical == "incoherente":
                # Añade alerta de alta severidad.
                hallazgos.append(
                    crear_hallazgo(
                        tipo="indexación",
                        descripcion="Canonical realmente incoherente respecto a la URL final indexable.",
                        recomendacion="Alinear canonical con la URL canónica estratégica y corregir enlazado interno relacionado.",
                    )
                )

        # Revisa imágenes sin atributo alt para accesibilidad y SEO semántico.
        for imagen in html.find_all("img"):
            # Obtiene atributo alt cuando exista.
            alt = (imagen.get("alt") or "").strip()

            # Señala imagen sin alt explícito.
            if not alt:
                # Añade hallazgo de contenido por accesibilidad/SEO.
                hallazgos.append(
                    crear_hallazgo(
                        tipo="contenido",
                        descripcion="Imagen sin atributo alt detectada.",
                        recomendacion="Añadir texto alt descriptivo y contextual en todas las imágenes informativas.",
                    )
                )
                # Limita ruido de hallazgos repetidos por página.
                break

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
