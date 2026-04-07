# Importa utilidades para gestión robusta de fechas y rutas.
from datetime import date, timedelta

# Importa Path para validar rutas de credenciales de forma portable.
from pathlib import Path

# Importa tipos para tipado estático explícito.
from typing import Any

# Importa tipos de configuración y dominio del proyecto.
from seo_auditor.config import Configuracion

# Importa modelos tipados para transportar datos de GA4.
from seo_auditor.models import DatosAnalytics, MetricaAnalyticsPagina, ResumenAnalytics

# Define umbrales de calidad alta para tráfico/engagement.
CALIDAD_ALTA_MIN_SESIONES = 30.0
CALIDAD_ALTA_MAX_REBOTE = 0.45
CALIDAD_ALTA_MIN_DURACION = 90.0
CALIDAD_ALTA_MIN_CONVERSIONES = 0.0

# Define umbrales de calidad baja para tráfico/engagement.
CALIDAD_BAJA_MAX_REBOTE = 0.7
CALIDAD_BAJA_MIN_DURACION = 35.0
CALIDAD_BAJA_MIN_SESIONES_SIN_CONVERSION = 20.0


# Convierte string YYYY-MM-DD a fecha validada.
def _parsear_fecha_iso(valor: str, etiqueta: str) -> date:
    """Valida y convierte una fecha ISO para consultas de GA4."""

    # Intenta parsear la fecha en formato ISO estricto.
    try:
        # Devuelve fecha parseada cuando el formato es correcto.
        return date.fromisoformat(valor)

    # Captura errores de formato con mensaje claro para operación.
    except ValueError as exc:
        # Propaga error con contexto de variable implicada.
        raise ValueError(f"{etiqueta} debe tener formato YYYY-MM-DD.") from exc


# Obtiene cliente autenticado de GA4 de forma perezosa.
def _crear_cliente_analytics_data(ruta_credenciales: Path) -> Any:
    """Crea cliente oficial de Google Analytics Data API v1."""

    # Importa cliente oficial de Analytics Data API en tiempo de ejecución.
    from google.analytics.data_v1beta import BetaAnalyticsDataClient

    # Crea cliente autenticado usando service account en archivo local.
    return BetaAnalyticsDataClient.from_service_account_file(str(ruta_credenciales))


# Valida y normaliza la ruta de página recibida desde GA4.
def _normalizar_ruta(ruta: str) -> str:
    """Normaliza rutas de GA4 para facilitar cruces con otras fuentes."""

    # Limpia espacios y aplica fallback de raíz.
    ruta_limpia = (ruta or "").strip() or "/"

    # Añade barra inicial para homogenizar rutas.
    return ruta_limpia if ruta_limpia.startswith("/") else f"/{ruta_limpia}"


# Calcula etiqueta cualitativa de calidad de tráfico.
def _calcular_calidad_trafico(sesiones: float, rebote: float, duracion_media: float, conversiones: float) -> str:
    """Devuelve alta/media/baja según comportamiento de usuario y conversión."""

    # Clasifica como alta calidad cuando combina engagement y conversión.
    if (
        sesiones >= CALIDAD_ALTA_MIN_SESIONES
        and rebote <= CALIDAD_ALTA_MAX_REBOTE
        and duracion_media >= CALIDAD_ALTA_MIN_DURACION
        and conversiones > CALIDAD_ALTA_MIN_CONVERSIONES
    ):
        # Retorna etiqueta alta.
        return "alta"

    # Clasifica como baja calidad cuando engagement y señales son débiles.
    if (
        rebote >= CALIDAD_BAJA_MAX_REBOTE
        or duracion_media < CALIDAD_BAJA_MIN_DURACION
        or (sesiones >= CALIDAD_BAJA_MIN_SESIONES_SIN_CONVERSION and conversiones <= 0)
    ):
        # Retorna etiqueta baja.
        return "baja"

    # Devuelve calidad media para casos intermedios.
    return "media"


# Consulta métricas por página de GA4 usando dimensión principal requerida.
def _consultar_metricas_paginas(
    cliente: Any,
    property_id: str,
    fecha_desde: str,
    fecha_hasta: str,
    limite: int,
) -> list[MetricaAnalyticsPagina]:
    """Consulta sesiones, usuarios, rebote, duración y conversiones por página."""

    # Importa clases de request del cliente oficial.
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

    # Ejecuta consulta principal por pagePath con métricas mínimas requeridas.
    respuesta = cliente.run_report(
        RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="conversions"),
            ],
            date_ranges=[DateRange(start_date=fecha_desde, end_date=fecha_hasta)],
            limit=limite,
        )
    )

    # Inicializa colección de métricas por página.
    paginas: list[MetricaAnalyticsPagina] = []

    # Recorre filas de la respuesta para mapearlas a modelos tipados.
    for fila in list(respuesta.rows or []):
        # Obtiene ruta de página desde dimensión principal.
        url = _normalizar_ruta(fila.dimension_values[0].value if fila.dimension_values else "")

        # Obtiene sesiones con fallback seguro.
        sesiones = float(fila.metric_values[0].value or 0.0)

        # Obtiene usuarios con fallback seguro.
        usuarios = float(fila.metric_values[1].value or 0.0)

        # Obtiene rebote decimal con fallback seguro.
        rebote = float(fila.metric_values[2].value or 0.0)

        # Obtiene duración media en segundos con fallback seguro.
        duracion_media = float(fila.metric_values[3].value or 0.0)

        # Obtiene conversiones con fallback seguro.
        conversiones = float(fila.metric_values[4].value or 0.0)

        # Añade fila tipada con calidad de tráfico derivada.
        paginas.append(
            MetricaAnalyticsPagina(
                url=url,
                sesiones=sesiones,
                usuarios=usuarios,
                rebote=rebote,
                duracion_media=duracion_media,
                conversiones=conversiones,
                calidad_trafico=_calcular_calidad_trafico(sesiones, rebote, duracion_media, conversiones),
            )
        )

    # Devuelve filas tipadas por página.
    return paginas


# Calcula resumen agregado ponderado desde filas por página.
def _calcular_resumen_analytics(paginas: list[MetricaAnalyticsPagina]) -> ResumenAnalytics:
    """Resume totales y promedios clave de comportamiento de usuario."""

    # Calcula sesiones totales del periodo.
    sesiones_totales = sum(item.sesiones for item in paginas)

    # Calcula usuarios totales del periodo.
    usuarios_totales = sum(item.usuarios for item in paginas)

    # Calcula conversiones totales del periodo.
    conversiones_totales = sum(item.conversiones for item in paginas)

    # Calcula rebote medio ponderado por sesiones.
    rebote_medio = (
        (sum(item.rebote * item.sesiones for item in paginas) / sesiones_totales) if sesiones_totales > 0 else 0.0
    )

    # Calcula duración media ponderada por sesiones.
    duracion_media = (
        (sum(item.duracion_media * item.sesiones for item in paginas) / sesiones_totales)
        if sesiones_totales > 0
        else 0.0
    )

    # Devuelve resumen agregado y redondeado.
    return ResumenAnalytics(
        sesiones_totales=round(sesiones_totales, 2),
        usuarios_totales=round(usuarios_totales, 2),
        rebote_medio=round(rebote_medio, 4),
        duracion_media=round(duracion_media, 2),
        conversiones=round(conversiones_totales, 2),
    )


# Carga datos de Analytics cuando la configuración esté completa.
def cargar_datos_analytics(configuracion: Configuracion) -> DatosAnalytics:
    """Obtiene datos autenticados de GA4 con degradación elegante."""

    # Devuelve objeto inactivo cuando la integración esté deshabilitada.
    if not configuracion.ga_enabled:
        # Retorna estado inactivo explícito.
        return DatosAnalytics(activo=False, error="Analytics desactivado por configuración.")

    # Valida presencia de property id configurado.
    if not configuracion.ga_property_id:
        # Retorna error controlado por configuración incompleta.
        return DatosAnalytics(activo=False, error="Falta GA_PROPERTY_ID en entorno.")

    # Valida que property id tenga formato numérico esperable.
    if not configuracion.ga_property_id.isdigit():
        # Retorna error controlado sin romper ejecución.
        return DatosAnalytics(activo=False, error="GA_PROPERTY_ID debe ser numérico.")

    # Valida presencia de ruta de credenciales.
    if not configuracion.ga_credentials_file:
        # Retorna error controlado por configuración incompleta.
        return DatosAnalytics(activo=False, error="Falta GA_CREDENTIALS_FILE en entorno.")

    # Construye ruta de credenciales desde configuración.
    ruta_credenciales = Path(configuracion.ga_credentials_file).expanduser()

    # Valida existencia de archivo de credenciales.
    if not ruta_credenciales.exists() or not ruta_credenciales.is_file():
        # Retorna error accionable sin romper ejecución.
        return DatosAnalytics(activo=False, error=f"No existe archivo de credenciales GA4: {ruta_credenciales}")

    # Inicializa fechas efectivas desde configuración.
    fecha_desde = configuracion.ga_date_from

    # Inicializa fecha fin efectiva desde configuración.
    fecha_hasta = configuracion.ga_date_to

    # Resuelve fecha fin automática cuando no esté definida.
    if not fecha_hasta:
        # Calcula fecha de ayer para evitar latencia intradía de datos.
        fecha_hasta = (date.today() - timedelta(days=1)).isoformat()

    # Resuelve fecha inicio automática cuando no esté definida.
    if not fecha_desde:
        # Calcula ventana de 28 días de forma conservadora.
        fecha_desde = date.fromordinal(date.fromisoformat(fecha_hasta).toordinal() - 28).isoformat()

    # Valida rango de fechas antes de consultar API.
    fecha_inicio_dt = _parsear_fecha_iso(fecha_desde, "GA_DATE_FROM")

    # Valida fecha de fin antes de consultar API.
    fecha_fin_dt = _parsear_fecha_iso(fecha_hasta, "GA_DATE_TO")

    # Verifica coherencia temporal básica del rango.
    if fecha_inicio_dt > fecha_fin_dt:
        # Retorna error claro de rango inválido.
        return DatosAnalytics(activo=False, error="GA_DATE_FROM no puede ser mayor que GA_DATE_TO.")

    # Intenta autenticar y consultar datos en bloque controlado.
    try:
        # Crea cliente oficial autenticado de GA4.
        cliente = _crear_cliente_analytics_data(ruta_credenciales)

        # Consulta métricas mínimas por página.
        paginas = _consultar_metricas_paginas(
            cliente,
            configuracion.ga_property_id,
            fecha_desde,
            fecha_hasta,
            configuracion.ga_row_limit,
        )

    # Maneja errores de autenticación/permisos/propiedad de forma no bloqueante.
    except Exception as exc:
        # Devuelve error accionable sin detener auditoría técnica.
        return DatosAnalytics(activo=False, error=f"Error al consultar Google Analytics 4: {exc}")

    # Devuelve dataset consolidado de Analytics.
    return DatosAnalytics(
        activo=True,
        error=None,
        property_id=configuracion.ga_property_id,
        date_from=fecha_desde,
        date_to=fecha_hasta,
        paginas=paginas,
        resumen=_calcular_resumen_analytics(paginas),
    )
