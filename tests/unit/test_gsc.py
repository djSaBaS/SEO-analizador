# Importa utilidades de fecha para validaciones deterministas.
from datetime import date, timedelta

# Importa módulo GSC bajo prueba.
from seo_auditor import gsc

# Importa configuración tipada del proyecto.
from seo_auditor.config import Configuracion


# Construye configuración base para pruebas de GSC.
def _configuracion_base() -> Configuracion:
    """Devuelve configuración mínima válida para pruebas de integración GSC."""

    # Devuelve objeto de configuración con GSC activo.
    return Configuracion(
        gemini_api_key="",
        gemini_model="gemini-2.5-flash",
        pagespeed_api_key="",
        http_timeout=10,
        max_urls=10,
        max_pagepsi_urls=5,
        pagespeed_timeout=45,
        pagespeed_reintentos=2,
        cache_ttl_segundos=21600,
        gsc_enabled=True,
        gsc_site_url="https://ejemplo.com/",
        gsc_credentials_file="./credenciales/falso.json",
        gsc_date_from="",
        gsc_date_to="",
        gsc_row_limit=250,
        ga_enabled=False,
        ga_property_id="",
        ga_credentials_file="",
        ga_date_from="",
        ga_date_to="",
        ga_row_limit=1000,
    )


# Verifica que la fecha final por defecto use ayer para evitar datos incompletos.
def test_cargar_datos_search_console_fecha_fin_por_defecto_es_ayer(monkeypatch, tmp_path) -> None:
    """Comprueba que GSC use ayer cuando no se define `GSC_DATE_TO`."""

    # Crea archivo de credenciales ficticio para pasar validación de ruta.
    credenciales = tmp_path / "credenciales.json"

    # Escribe JSON mínimo de prueba para que exista el archivo.
    credenciales.write_text("{}", encoding="utf-8")

    # Construye configuración base con ruta temporal de credenciales.
    configuracion = _configuracion_base()

    # Actualiza ruta de credenciales para la prueba.
    configuracion.gsc_credentials_file = str(credenciales)

    # Inyecta servicio falso sin dependencias externas.
    monkeypatch.setattr(gsc, "_crear_servicio_search_console", lambda *_args, **_kwargs: object())

    # Define consulta simulada vacía para todas las dimensiones.
    monkeypatch.setattr(gsc, "_consultar_search_analytics", lambda *_args, **_kwargs: [])

    # Ejecuta carga de datos GSC.
    datos = gsc.cargar_datos_search_console(configuracion)

    # Calcula fecha esperada de ayer en formato ISO.
    fecha_esperada = (date.today() - timedelta(days=1)).isoformat()

    # Verifica que la fecha final resuelta sea ayer.
    assert datos.date_to == fecha_esperada


# Verifica que el mapping query->URL se complete con el cruce query+page.
def test_cargar_datos_search_console_completa_url_asociada_en_queries(monkeypatch, tmp_path) -> None:
    """Comprueba que `url_asociada` se rellene con la URL principal por query."""

    # Crea archivo de credenciales ficticio para pasar validación de ruta.
    credenciales = tmp_path / "credenciales.json"

    # Escribe JSON mínimo de prueba para que exista el archivo.
    credenciales.write_text("{}", encoding="utf-8")

    # Construye configuración base con ruta temporal de credenciales.
    configuracion = _configuracion_base()

    # Actualiza ruta de credenciales para la prueba.
    configuracion.gsc_credentials_file = str(credenciales)

    # Inyecta servicio falso sin dependencias externas.
    monkeypatch.setattr(gsc, "_crear_servicio_search_console", lambda *_args, **_kwargs: object())

    # Define respuesta simulada por dimensión solicitada.
    def _consulta_simulada(_servicio, _site_url, _desde, _hasta, dimensiones, _limite, _tipo="web"):
        """Devuelve filas sintéticas por dimensión para validar mapping."""

        # Devuelve filas por página para el bloque de páginas.
        if dimensiones == ["page"]:
            # Retorna una URL con visibilidad.
            return [
                {"keys": ["https://ejemplo.com/url-a"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 7.0}
            ]

        # Devuelve filas por query para el bloque de queries.
        if dimensiones == ["query"]:
            # Retorna query principal de prueba.
            return [{"keys": ["consulta prueba"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 7.0}]

        # Devuelve cruce query+page para resolver URL asociada.
        if dimensiones == ["query", "page"]:
            # Retorna query asociada a URL concreta.
            return [{"keys": ["consulta prueba", "https://ejemplo.com/url-a"], "clicks": 10, "impressions": 100}]

        # Devuelve vacío para dimensiones opcionales.
        return []

    # Inyecta consulta simulada en el módulo GSC.
    monkeypatch.setattr(gsc, "_consultar_search_analytics", _consulta_simulada)

    # Ejecuta carga de datos GSC.
    datos = gsc.cargar_datos_search_console(configuracion)

    # Verifica que exista al menos una query exportable.
    assert datos.queries

    # Verifica que la query tenga URL asociada desde el cruce query+page.
    assert datos.queries[0].url_asociada == "https://ejemplo.com/url-a"
