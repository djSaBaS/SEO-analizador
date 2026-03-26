# Importa utilidades de tipos para construir argumentos simulados.
from types import SimpleNamespace

# Importa módulo CLI bajo prueba.
from seo_auditor import cli

# Importa configuración tipada del proyecto.
from seo_auditor.config import Configuracion

# Importa modelos tipados de integración externa.
from seo_auditor.models import DatosAnalytics, DatosSearchConsole


# Construye configuración base para los modos de prueba de conectividad.
def _configuracion_base() -> Configuracion:
    """Devuelve configuración mínima válida para pruebas de modos testga/testgsc."""

    # Devuelve objeto de configuración consistente para el CLI.
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
        gsc_credentials_file="/tmp/falso-gsc.json",
        gsc_date_from="",
        gsc_date_to="",
        gsc_row_limit=250,
        ga_enabled=True,
        ga_property_id="123456",
        ga_credentials_file="/tmp/falso-ga.json",
        ga_date_from="",
        ga_date_to="",
        ga_row_limit=1000,
    )


# Verifica que --testga no requiera sitemap y termine en éxito.
def test_main_testga_ok_sin_sitemap(monkeypatch) -> None:
    """Comprueba que `--testga` valide conectividad sin ejecutar auditoría completa."""

    # Construye argumentos de modo test GA4 sin sitemap.
    argumentos = SimpleNamespace(
        sitemap="",
        output="",
        usar_ia=False,
        testia=False,
        testga=True,
        testgsc=False,
        modelo_ia="",
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        gestor="Gestor",
        max_muestras_ia=5,
        modo="completo",
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
        noGSC=False,
        date_from="",
        date_to="",
        generar_todo=False,
        comparar="periodo-anterior",
        provincia="",
        cliente="",
    )

    # Define parser simulado para evitar CLI real.
    class _ParserFalso:
        """Parser mínimo que devuelve argumentos simulados."""

        # Devuelve argumentos preconstruidos.
        def parse_args(self):
            """Retorna argumentos simulados de forma estable."""
            return argumentos

    # Inyecta parser falso en el módulo CLI.
    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())

    # Inyecta configuración base estable.
    monkeypatch.setattr(cli, "cargar_configuracion", _configuracion_base)

    # Simula respuesta exitosa de Analytics.
    monkeypatch.setattr(
        cli,
        "cargar_datos_analytics",
        lambda *_args, **_kwargs: DatosAnalytics(
            activo=True,
            error=None,
            property_id="123456",
            date_from="2026-02-01",
            date_to="2026-02-28",
            paginas=[],
        ),
    )

    # Protege contra ejecución accidental de flujo completo.
    monkeypatch.setattr(cli, "extraer_urls_sitemap", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("No debe extraer sitemap en --testga")))

    # Ejecuta flujo principal.
    codigo = cli.main()

    # Verifica ejecución correcta en modo de prueba.
    assert codigo == 0


# Verifica que --testgsc no requiera sitemap y reporte error cuando falle.
def test_main_testgsc_error_sin_sitemap(monkeypatch) -> None:
    """Comprueba que `--testgsc` falle con código 1 cuando no hay conexión útil."""

    # Construye argumentos de modo test GSC sin sitemap.
    argumentos = SimpleNamespace(
        sitemap="",
        output="",
        usar_ia=False,
        testia=False,
        testga=False,
        testgsc=True,
        modelo_ia="",
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        gestor="Gestor",
        max_muestras_ia=5,
        modo="completo",
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
        noGSC=False,
        date_from="",
        date_to="",
        generar_todo=False,
        comparar="periodo-anterior",
        provincia="",
        cliente="",
    )

    # Define parser simulado para evitar CLI real.
    class _ParserFalso:
        """Parser mínimo que devuelve argumentos simulados."""

        # Devuelve argumentos preconstruidos.
        def parse_args(self):
            """Retorna argumentos simulados de forma estable."""
            return argumentos

    # Inyecta parser falso en el módulo CLI.
    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())

    # Inyecta configuración base estable.
    monkeypatch.setattr(cli, "cargar_configuracion", _configuracion_base)

    # Simula respuesta fallida de Search Console.
    monkeypatch.setattr(
        cli,
        "cargar_datos_search_console",
        lambda *_args, **_kwargs: DatosSearchConsole(
            activo=False,
            error="Error al consultar Search Console: 403 Forbidden",
            site_url="https://ejemplo.com/",
            date_from="2026-02-01",
            date_to="2026-02-28",
            paginas=[],
            queries=[],
            filas_query_pagina=[],
            filas_dispositivo=[],
            filas_pais=[],
        ),
    )

    # Protege contra ejecución accidental de flujo completo.
    monkeypatch.setattr(cli, "extraer_urls_sitemap", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("No debe extraer sitemap en --testgsc")))

    # Ejecuta flujo principal.
    codigo = cli.main()

    # Verifica error esperado en modo de prueba fallido.
    assert codigo == 1


# Verifica que --testga aplique --date-from/--date-to antes de consultar GA4.
def test_main_testga_aplica_rango_fechas_cli(monkeypatch) -> None:
    """Comprueba que la prueba de conectividad use el rango temporal indicado por CLI."""

    # Construye argumentos de modo test GA4 con rango explícito.
    argumentos = SimpleNamespace(
        sitemap="",
        output="",
        usar_ia=False,
        testia=False,
        testga=True,
        testgsc=False,
        modelo_ia="",
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        gestor="Gestor",
        max_muestras_ia=5,
        modo="completo",
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
        noGSC=False,
        date_from="2026-01-01",
        date_to="2026-01-31",
        generar_todo=False,
        comparar="periodo-anterior",
        provincia="",
        cliente="",
    )

    # Define parser simulado para evitar CLI real.
    class _ParserFalso:
        """Parser mínimo que devuelve argumentos simulados."""

        # Devuelve argumentos preconstruidos.
        def parse_args(self):
            """Retorna argumentos simulados de forma estable."""
            return argumentos

    # Inyecta parser falso en el módulo CLI.
    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())

    # Inyecta configuración base estable.
    monkeypatch.setattr(cli, "cargar_configuracion", _configuracion_base)

    # Simula carga GA4 verificando el rango recibido en configuración.
    def _carga_ga4_verificando_rango(configuracion):
        """Valida que el helper haya aplicado fechas CLI a la configuración efectiva."""
        assert configuracion.ga_date_from == "2026-01-01"
        assert configuracion.ga_date_to == "2026-01-31"
        return DatosAnalytics(activo=True, error=None, property_id="123456", date_from="2026-01-01", date_to="2026-01-31", paginas=[])

    # Inyecta simulador GA4 con aserciones de rango.
    monkeypatch.setattr(cli, "cargar_datos_analytics", _carga_ga4_verificando_rango)

    # Ejecuta flujo principal.
    codigo = cli.main()

    # Verifica éxito en modo de prueba.
    assert codigo == 0
