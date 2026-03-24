# Importa utilidades para gestión robusta de fechas y rutas.
from datetime import date

# Importa Path para validar rutas de credenciales de forma portable.
from pathlib import Path

# Importa tipos para tipado estático explícito.
from typing import Any

# Importa tipos de configuración y dominio del proyecto.
from seo_auditor.config import Configuracion

# Importa modelos tipados para transportar datos de GSC.
from seo_auditor.models import DatosSearchConsole, MetricaGscPagina, MetricaGscQuery


# Convierte string YYYY-MM-DD a fecha validada.
def _parsear_fecha_iso(valor: str, etiqueta: str) -> date:
    """Valida y convierte una fecha ISO para consultas de Search Console."""

    # Intenta parsear la fecha en formato ISO estricto.
    try:
        # Devuelve fecha parseada cuando el formato es correcto.
        return date.fromisoformat(valor)

    # Captura errores de formato con mensaje claro para operación.
    except ValueError as exc:
        # Propaga error con contexto de variable implicada.
        raise ValueError(f"{etiqueta} debe tener formato YYYY-MM-DD.") from exc


# Obtiene cliente autenticado de Search Console de forma perezosa.
def _crear_servicio_search_console(ruta_credenciales: Path) -> Any:
    """Crea el cliente oficial de Search Console usando service account."""

    # Importa credenciales de Google de forma dinámica para dependencia opcional.
    from google.oauth2.service_account import Credentials

    # Importa builder del cliente oficial de Google APIs.
    from googleapiclient.discovery import build

    # Define scope mínimo requerido para lectura de Search Console.
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]

    # Carga credenciales desde archivo JSON configurado.
    credenciales = Credentials.from_service_account_file(str(ruta_credenciales), scopes=scopes)

    # Crea servicio oficial de Search Console versión v3.
    return build("searchconsole", "v1", credentials=credenciales, cache_discovery=False)


# Convierte una fila API en métrica por página tipada.
def _fila_a_metrica_pagina(fila: dict[str, Any]) -> MetricaGscPagina:
    """Mapea una fila de API en estructura tipada por página."""

    # Obtiene URL de dimensión principal cuando exista.
    url = str((fila.get("keys") or [""])[0]).strip()

    # Devuelve métrica tipada con valores defensivos.
    return MetricaGscPagina(
        url=url,
        clicks=float(fila.get("clicks", 0.0) or 0.0),
        impresiones=float(fila.get("impressions", 0.0) or 0.0),
        ctr=float(fila.get("ctr", 0.0) or 0.0),
        posicion_media=float(fila.get("position", 0.0) or 0.0),
        dispositivo="",
        pais="",
    )


# Convierte una fila API en métrica por query tipada.
def _fila_a_metrica_query(fila: dict[str, Any]) -> MetricaGscQuery:
    """Mapea una fila de API en estructura tipada por query."""

    # Obtiene query como primera dimensión disponible.
    query = str((fila.get("keys") or [""])[0]).strip()

    # Devuelve métrica tipada con valores defensivos.
    return MetricaGscQuery(
        query=query,
        clicks=float(fila.get("clicks", 0.0) or 0.0),
        impresiones=float(fila.get("impressions", 0.0) or 0.0),
        ctr=float(fila.get("ctr", 0.0) or 0.0),
        posicion_media=float(fila.get("position", 0.0) or 0.0),
        url_asociada="",
    )


# Ejecuta consulta estándar de Search Console con control de errores.
def _consultar_search_analytics(
    servicio: Any,
    site_url: str,
    fecha_desde: str,
    fecha_hasta: str,
    dimensiones: list[str],
    limite: int,
    tipo: str = "web",
) -> list[dict[str, Any]]:
    """Consulta Search Analytics y devuelve filas crudas cuando existan."""

    # Construye payload oficial para consulta.
    cuerpo = {
        "startDate": fecha_desde,
        "endDate": fecha_hasta,
        "dimensions": dimensiones,
        "rowLimit": limite,
        "type": tipo,
    }

    # Ejecuta consulta oficial contra Search Console.
    respuesta = servicio.searchanalytics().query(siteUrl=site_url, body=cuerpo).execute()

    # Devuelve filas o lista vacía cuando no existan datos.
    return list(respuesta.get("rows", []) or [])


# Carga datos de Search Console cuando la configuración esté completa.
def cargar_datos_search_console(configuracion: Configuracion) -> DatosSearchConsole:
    """Obtiene datos autenticados de GSC con degradación elegante."""

    # Devuelve objeto inactivo cuando la integración esté deshabilitada.
    if not configuracion.gsc_enabled:
        # Retorna estado inactivo explícito.
        return DatosSearchConsole(activo=False, error="GSC desactivado por configuración.")

    # Valida presencia de site URL configurado.
    if not configuracion.gsc_site_url:
        # Retorna error controlado por configuración incompleta.
        return DatosSearchConsole(activo=False, error="Falta GSC_SITE_URL en entorno.")

    # Valida presencia de ruta de credenciales.
    if not configuracion.gsc_credentials_file:
        # Retorna error controlado por configuración incompleta.
        return DatosSearchConsole(activo=False, error="Falta GSC_CREDENTIALS_FILE en entorno.")

    # Construye ruta de credenciales desde configuración.
    ruta_credenciales = Path(configuracion.gsc_credentials_file).expanduser()

    # Valida existencia de archivo de credenciales.
    if not ruta_credenciales.exists() or not ruta_credenciales.is_file():
        # Retorna error accionable sin romper ejecución.
        return DatosSearchConsole(activo=False, error=f"No existe archivo de credenciales GSC: {ruta_credenciales}")

    # Inicializa fechas efectivas desde configuración.
    fecha_desde = configuracion.gsc_date_from

    # Inicializa fecha fin efectiva desde configuración.
    fecha_hasta = configuracion.gsc_date_to

    # Resuelve fecha fin automática cuando no esté definida.
    if not fecha_hasta:
        # Calcula fecha de ayer para evitar datos incompletos del día actual.
        fecha_hasta = (date.today()).isoformat()

    # Resuelve fecha inicio automática cuando no esté definida.
    if not fecha_desde:
        # Calcula ventana de 28 días de forma conservadora.
        fecha_desde = date.fromordinal(date.fromisoformat(fecha_hasta).toordinal() - 28).isoformat()

    # Valida rango de fechas antes de consultar API.
    fecha_inicio_dt = _parsear_fecha_iso(fecha_desde, "GSC_DATE_FROM")

    # Valida fecha de fin antes de consultar API.
    fecha_fin_dt = _parsear_fecha_iso(fecha_hasta, "GSC_DATE_TO")

    # Verifica coherencia temporal básica del rango.
    if fecha_inicio_dt > fecha_fin_dt:
        # Retorna error claro de rango inválido.
        return DatosSearchConsole(activo=False, error="GSC_DATE_FROM no puede ser mayor que GSC_DATE_TO.")

    # Intenta autenticar y consultar datos en bloque controlado.
    try:
        # Construye servicio oficial autenticado.
        servicio = _crear_servicio_search_console(ruta_credenciales)

        # Consulta rendimiento agregado por página.
        filas_paginas = _consultar_search_analytics(
            servicio,
            configuracion.gsc_site_url,
            fecha_desde,
            fecha_hasta,
            ["page"],
            configuracion.gsc_row_limit,
            "web",
        )

        # Consulta rendimiento agregado por query.
        filas_queries = _consultar_search_analytics(
            servicio,
            configuracion.gsc_site_url,
            fecha_desde,
            fecha_hasta,
            ["query"],
            configuracion.gsc_row_limit,
            "web",
        )

        # Consulta cruce query+page para mapear oportunidad por URL.
        filas_query_pagina = _consultar_search_analytics(
            servicio,
            configuracion.gsc_site_url,
            fecha_desde,
            fecha_hasta,
            ["query", "page"],
            configuracion.gsc_row_limit,
            "web",
        )

        # Inicializa agregados opcionales por dispositivo.
        filas_dispositivo: list[dict[str, Any]] = []

        # Inicializa agregados opcionales por país.
        filas_pais: list[dict[str, Any]] = []

        # Intenta cargar desglose por dispositivo sin bloquear flujo principal.
        try:
            # Ejecuta consulta por dispositivo en web search.
            filas_dispositivo = _consultar_search_analytics(
                servicio,
                configuracion.gsc_site_url,
                fecha_desde,
                fecha_hasta,
                ["device"],
                min(50, configuracion.gsc_row_limit),
                "web",
            )
        except Exception:
            # Mantiene lista vacía cuando no esté disponible.
            filas_dispositivo = []

        # Intenta cargar desglose por país sin bloquear flujo principal.
        try:
            # Ejecuta consulta por país en web search.
            filas_pais = _consultar_search_analytics(
                servicio,
                configuracion.gsc_site_url,
                fecha_desde,
                fecha_hasta,
                ["country"],
                min(100, configuracion.gsc_row_limit),
                "web",
            )
        except Exception:
            # Mantiene lista vacía cuando no esté disponible.
            filas_pais = []

    # Maneja errores de autenticación/permisos/propiedad de forma no bloqueante.
    except Exception as exc:
        # Devuelve error accionable sin detener auditoría técnica.
        return DatosSearchConsole(activo=False, error=f"Error al consultar Search Console: {exc}")

    # Convierte filas por página a modelos tipados.
    paginas = [_fila_a_metrica_pagina(fila) for fila in filas_paginas]

    # Convierte filas por query a modelos tipados.
    queries = [_fila_a_metrica_query(fila) for fila in filas_queries]

    # Devuelve dataset consolidado de Search Console.
    return DatosSearchConsole(
        activo=True,
        error=None,
        site_url=configuracion.gsc_site_url,
        date_from=fecha_desde,
        date_to=fecha_hasta,
        paginas=paginas,
        queries=queries,
        filas_query_pagina=filas_query_pagina,
        filas_dispositivo=filas_dispositivo,
        filas_pais=filas_pais,
    )
