# Importa utilidades de fecha para validaciones deterministas.
from datetime import date, timedelta

# Importa configuración tipada del proyecto.
from seo_auditor.config import Configuracion

# Importa módulo GA4 bajo prueba.
from seo_auditor import ga4


# Construye configuración base para pruebas de GA4.
def _configuracion_base() -> Configuracion:
    """Devuelve configuración mínima válida para pruebas de integración GA4."""

    # Devuelve objeto de configuración con GA4 activo.
    return Configuracion(
        gemini_api_key="",
        gemini_model="gemini-2.0-flash",
        pagespeed_api_key="",
        http_timeout=10,
        max_urls=10,
        max_pagepsi_urls=5,
        pagespeed_timeout=45,
        pagespeed_reintentos=2,
        cache_ttl_segundos=21600,
        gsc_enabled=False,
        gsc_site_url="",
        gsc_credentials_file="",
        gsc_date_from="",
        gsc_date_to="",
        gsc_row_limit=250,
        ga_enabled=True,
        ga_property_id="123456",
        ga_credentials_file="./credenciales/falso.json",
        ga_date_from="",
        ga_date_to="",
        ga_row_limit=1000,
    )


# Verifica fecha final por defecto para GA4 cuando no se define GA_DATE_TO.
def test_cargar_datos_analytics_fecha_fin_por_defecto_es_ayer(monkeypatch, tmp_path) -> None:
    """Comprueba que GA4 use ayer cuando no se define `GA_DATE_TO`."""

    # Crea archivo de credenciales ficticio para pasar validación de ruta.
    credenciales = tmp_path / "credenciales.json"

    # Escribe JSON mínimo de prueba para que exista el archivo.
    credenciales.write_text("{}", encoding="utf-8")

    # Construye configuración base con ruta temporal de credenciales.
    configuracion = _configuracion_base()

    # Actualiza ruta de credenciales para la prueba.
    configuracion.ga_credentials_file = str(credenciales)

    # Inyecta cliente falso sin dependencias externas.
    monkeypatch.setattr(ga4, "_crear_cliente_analytics_data", lambda *_args, **_kwargs: object())

    # Inyecta consulta simulada sin filas de página.
    monkeypatch.setattr(ga4, "_consultar_metricas_paginas", lambda *_args, **_kwargs: [])

    # Ejecuta carga de datos GA4.
    datos = ga4.cargar_datos_analytics(configuracion)

    # Calcula fecha esperada de ayer en formato ISO.
    fecha_esperada = (date.today() - timedelta(days=1)).isoformat()

    # Verifica fecha final y activación del bloque de Analytics.
    assert datos.date_to == fecha_esperada
    assert datos.activo is True


# Verifica cálculo de calidad de tráfico con reglas principales.
def test_calcular_calidad_trafico() -> None:
    """Comprueba etiqueta de calidad alta, media y baja según comportamiento."""

    # Verifica clasificación de alta calidad de tráfico.
    assert ga4._calcular_calidad_trafico(120, 0.35, 140, 2) == "alta"

    # Verifica clasificación de baja calidad de tráfico.
    assert ga4._calcular_calidad_trafico(90, 0.78, 22, 0) == "baja"

    # Verifica clasificación media en caso intermedio.
    assert ga4._calcular_calidad_trafico(45, 0.52, 70, 1) == "media"
