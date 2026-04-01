"""Escenarios de equivalencia CLI vs servicio de auditoría."""

from types import SimpleNamespace

from seo_auditor import cli
from seo_auditor.models import ResultadoAuditoria, ResultadoUrl
from seo_auditor.services.auditoria_service import AuditoriaService, construir_request_desde_cli
from seo_auditor.services.entregables_service import ENTREGABLES_BASE_AUDITORIA


class _Cfg:
    gemini_api_key = ""
    gemini_model = "gemini-2.5-flash"
    pagespeed_api_key = ""
    http_timeout = 10
    max_urls = 10
    max_pagepsi_urls = 5
    pagespeed_timeout = 45
    pagespeed_reintentos = 1
    cache_ttl_segundos = 60
    gsc_enabled = False
    gsc_site_url = ""
    gsc_credentials_file = ""
    gsc_date_from = ""
    gsc_date_to = ""
    gsc_row_limit = 250
    ga_enabled = False
    ga_property_id = ""
    ga_credentials_file = ""
    ga_date_from = ""
    ga_date_to = ""
    ga_row_limit = 1000


def _resultado_base() -> ResultadoAuditoria:
    return ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[
            ResultadoUrl(
                url="https://ejemplo.com/",
                tipo="page",
                estado_http=200,
                redirecciona=False,
                url_final="https://ejemplo.com/",
                title="Inicio",
                h1="Inicio",
                meta_description="Meta",
                canonical="https://ejemplo.com/",
                noindex=False,
                hallazgos=[],
            )
        ],
        cliente="Ejemplo",
        fecha_ejecucion="2026-04-01",
        gestor="Gestor",
    )


def test_equivalencia_estructural_cli_vs_servicio(monkeypatch, tmp_path) -> None:
    """Compara salidas estructurales clave entre flujo CLI y contrato de servicio."""
    argumentos = SimpleNamespace(
        sitemap="https://ejemplo.com/sitemap.xml",
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
        modo="completo",
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
        noGSC=False,
        comparar="periodo-anterior",
        provincia="",
        date_from="2026-03-01",
        date_to="2026-03-31",
        generar_todo=False,
    )

    class _ParserFalso:
        def parse_args(self):
            return argumentos

    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())
    monkeypatch.setattr(cli, "cargar_configuracion", lambda: _Cfg())
    monkeypatch.setattr(cli, "extraer_urls_sitemap", lambda *_a, **_k: ["https://ejemplo.com/"])
    monkeypatch.setattr(cli, "auditar_urls", lambda *_a, **_k: _resultado_base())
    monkeypatch.setattr(cli, "analizar_indexacion_rastreo", lambda *_a, **_k: {})
    monkeypatch.setattr(cli, "generar_gestion_indexacion_inteligente", lambda *_a, **_k: [])

    capturado = {}

    def _capturar_json(resultado, _path):
        capturado["cli"] = resultado
        return _path

    monkeypatch.setattr(cli, "exportar_json", _capturar_json)
    monkeypatch.setattr(cli, "exportar_excel", lambda *_a, **_k: None)
    monkeypatch.setattr(cli, "exportar_word", lambda *_a, **_k: None)
    monkeypatch.setattr(cli, "exportar_pdf", lambda *_a, **_k: None)
    monkeypatch.setattr(cli, "exportar_html", lambda *_a, **_k: None)
    monkeypatch.setattr(cli, "exportar_markdown_ia", lambda *_a, **_k: None)

    codigo_cli = cli.main()

    cfg = _Cfg()
    request = construir_request_desde_cli(
        argumentos,
        cfg,
        modelo_ia=cfg.gemini_model,
        periodo_desde="2026-03-01",
        periodo_hasta="2026-03-31",
        perfil_generacion="auditoria-seo-completa",
    )
    servicio = AuditoriaService(cli._crear_adaptadores_temporales())
    contrato = servicio.ejecutar_contrato(request)

    assert codigo_cli == 0
    assert contrato.resumen_ejecucion.codigo_salida == 0
    assert capturado["cli"].sitemap == contrato.auditoria.sitemap
    assert len(capturado["cli"].resultados) == len(contrato.auditoria.resultados)
    assert set(contrato.entregables.generados) == set(ENTREGABLES_BASE_AUDITORIA)
