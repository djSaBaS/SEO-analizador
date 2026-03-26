# Importa utilidades para crear argumentos simulados del CLI.
from types import SimpleNamespace

# Importa módulo CLI bajo prueba.
from seo_auditor import cli

# Importa configuración tipada del proyecto.
from seo_auditor.config import Configuracion


# Construye una configuración base para pruebas del modo GA4 premium.
def _configuracion_base() -> Configuracion:
    """Devuelve configuración mínima válida para ejecutar el modo dedicado."""

    # Retorna configuración consistente con GA4 habilitado.
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
        gsc_enabled=False,
        gsc_site_url="",
        gsc_credentials_file="",
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


# Verifica que el modo informe-ga4 no requiera sitemap y termine en éxito.
def test_main_modo_informe_ga4_ejecuta_exportador(monkeypatch, tmp_path) -> None:
    """Comprueba que el CLI use el generador premium sin entrar en auditoría SEO."""

    # Construye argumentos del modo dedicado GA4.
    argumentos = SimpleNamespace(
        sitemap="",
        output=str(tmp_path),
        usar_ia=False,
        testia=False,
        testga=False,
        testgsc=False,
        modelo_ia="",
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        gestor="Gestor",
        cliente="",
        max_muestras_ia=5,
        modo="informe-ga4",
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
        noGSC=False,
        comparar="periodo-anterior",
        provincia="Madrid",
        date_from="2026-03-01",
        date_to="2026-03-20",
    )

    # Define parser falso para inyectar argumentos controlados.
    class _ParserFalso:
        """Parser mínimo que devuelve argumentos simulados."""

        # Devuelve argumentos preparados para la prueba.
        def parse_args(self):
            """Retorna argumentos simulados de forma estable."""
            return argumentos

    # Reemplaza parser real por parser falso.
    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())

    # Inyecta configuración base estable.
    monkeypatch.setattr(cli, "cargar_configuracion", _configuracion_base)

    # Define bandera de ejecución del exportador premium.
    estado = {"ejecutado": False}

    # Simula generación premium devolviendo rutas de salida.
    def _generador_falso(*_args, **_kwargs):
        """Marca ejecución y devuelve metadatos de salida simulados."""
        estado["ejecutado"] = True
        return {
            "activo": True,
            "html": str(tmp_path / "informe_ga4_premium.html"),
            "pdf": str(tmp_path / "informe_ga4_premium.pdf"),
            "excel": str(tmp_path / "informe_ga4_premium.xlsx"),
        }

    # Inyecta generador premium simulado.
    monkeypatch.setattr(cli, "generar_informe_ga4_premium", _generador_falso)

    # Protege contra ejecución accidental de auditoría de sitemap.
    monkeypatch.setattr(cli, "extraer_urls_sitemap", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("No debe analizar sitemap en modo informe-ga4")))

    # Ejecuta flujo principal del CLI.
    codigo = cli.main()

    # Verifica que el modo termina correctamente.
    assert codigo == 0

    # Verifica que el generador premium fue invocado.
    assert estado["ejecutado"] is True


# Verifica que el resolver de cliente soporte sitemap nulo sin romper.
def test_resolver_cliente_informe_ga4_con_sitemap_none() -> None:
    """Comprueba compatibilidad cuando `--sitemap` no se informa y queda en None."""

    # Ejecuta helper con valores nulos para reproducir el caso reportado.
    cliente = cli._resolver_cliente_informe_ga4("", None)

    # Verifica fallback seguro sin excepciones.
    assert cliente == "Cliente GA4"
