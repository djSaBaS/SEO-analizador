# Importa parser de URL para derivar robots.txt.
from urllib.parse import urlparse

# Importa utilidades para dependencias opcionales.
import importlib

# Importa utilidades de descubrimiento de módulos.
import importlib.util

# Importa cliente HTTP para validaciones de disponibilidad.
import requests

# Importa utilidades internas de normalización y validación.
from seo_auditor.utils import es_url_http_valida, normalizar_url


# Resuelve disponibilidad real de advertools en tiempo de ejecución.
ADVERTOOLS_DISPONIBLE = importlib.util.find_spec("advertools") is not None

# Carga módulo advertools solo cuando exista en entorno.
adv = importlib.import_module("advertools") if ADVERTOOLS_DISPONIBLE else None


# Deriva la URL de robots.txt a partir del sitemap base.
def _resolver_robots_url(sitemap_url: str) -> str:
    """Construye la ruta canónica de robots.txt para el dominio analizado."""

    # Parsea el sitemap para obtener esquema y host.
    parseada = urlparse(sitemap_url)

    # Devuelve robots.txt del dominio base.
    return f"{parseada.scheme}://{parseada.netloc}/robots.txt"


# Evalúa si una ruta está bloqueada por patrones básicos de robots.
def _esta_bloqueada_por_patrones(url: str, patrones_disallow: list[str]) -> bool:
    """Determina bloqueo simple mediante coincidencia de prefijo de ruta."""

    # Obtiene la ruta de la URL auditada.
    ruta_url = urlparse(url).path or "/"

    # Recorre cada patrón disallow detectado.
    for patron in patrones_disallow:
        # Limpia espacios para comparación robusta.
        patron_limpio = patron.strip()

        # Omite patrones vacíos.
        if not patron_limpio:
            # Continúa con el siguiente patrón válido.
            continue

        # Evalúa comodín global en robots.
        if patron_limpio == "/":
            # Marca bloqueo completo del dominio.
            return True

        # Evalúa coincidencia de prefijo de ruta.
        if ruta_url.startswith(patron_limpio):
            # Marca URL bloqueada por robots.
            return True

    # Devuelve no bloqueada cuando no hay coincidencias.
    return False


# Analiza indexación/rastreo usando robots y sitemap de forma tolerante.
def analizar_indexacion_rastreo(sitemap_url: str, urls_sitemap: list[str], timeout: int) -> dict[str, object]:
    """Devuelve un resumen de indexación y rastreo apto para informes ejecutivos."""

    # Inicializa estructura de respuesta por defecto.
    resumen: dict[str, object] = {
        "robots_url": "",
        "robots_disponible": False,
        "sitemap_valido": bool(urls_sitemap),
        "urls_bloqueadas": [],
        "incoherencias_sitemap_robots": [],
        "urls_huerfanas": [],
        "detalle_error": "",
    }

    # Evita análisis cuando sitemap no sea válido.
    if not es_url_http_valida(sitemap_url):
        # Registra error de parámetro.
        resumen["detalle_error"] = "Sitemap inválido para análisis de indexación."

        # Devuelve resumen mínimo seguro.
        return resumen

    # Resuelve URL de robots para el dominio objetivo.
    robots_url = _resolver_robots_url(sitemap_url)

    # Guarda URL de robots en el resumen.
    resumen["robots_url"] = robots_url

    # Intenta consultar robots para verificar disponibilidad real.
    try:
        # Ejecuta solicitud de robots.
        respuesta_robots = requests.get(robots_url, timeout=timeout)

        # Marca disponibilidad solo con HTTP exitoso.
        resumen["robots_disponible"] = respuesta_robots.status_code == 200
    except Exception as exc:
        # Registra error controlado de conectividad.
        resumen["detalle_error"] = f"No se pudo leer robots.txt: {exc}"

        # Devuelve resumen parcial sin romper ejecución.
        return resumen

    # Inicializa patrones disallow detectados.
    patrones_disallow: list[str] = []

    # Intenta parsear robots con advertools cuando esté disponible.
    if adv is not None:
        # Intenta parsear reglas robots con advertools.
        try:
            # Obtiene dataframe de reglas robots para el dominio.
            robots_df = adv.robotstxt_to_df(robots_url)

            # Recorre filas para extraer directivas disallow.
            for _, fila in robots_df.iterrows():
                # Lee campo directive por compatibilidad de versión.
                directiva = str(fila.get("directive", "")).strip().lower()

                # Lee campo content con la ruta afectada.
                contenido = str(fila.get("content", "")).strip()

                # Agrega solo directivas disallow con contenido útil.
                if directiva == "disallow" and contenido:
                    # Añade patrón detectado al conjunto.
                    patrones_disallow.append(contenido)
        except Exception:
            # Mantiene flujo incluso si advertools no puede parsear robots.
            patrones_disallow = []

    # Inicializa acumuladores de bloqueo detectado.
    urls_bloqueadas: list[str] = []

    # Recorre URLs del sitemap para validar coherencia con robots.
    for url in urls_sitemap:
        # Evalúa bloqueo por patrones básicos.
        if _esta_bloqueada_por_patrones(normalizar_url(url), patrones_disallow):
            # Añade URL bloqueada al listado.
            urls_bloqueadas.append(url)

    # Guarda URLs bloqueadas en el resumen.
    resumen["urls_bloqueadas"] = urls_bloqueadas

    # Reutiliza lista bloqueada como incoherencia principal.
    resumen["incoherencias_sitemap_robots"] = list(urls_bloqueadas)

    # Devuelve resumen completo de indexación/rastreo.
    return resumen
