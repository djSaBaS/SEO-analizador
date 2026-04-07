"""Pruebas de contrato para modelos y servicios principales."""

from types import SimpleNamespace

from seo_auditor.models import (
    AuditoriaRequest,
    AuditoriaResult,
    ResultadoAuditoria,
    ResultadoEntregables,
    ResumenEjecucion,
)
from seo_auditor.services.auditoria_service import construir_request_desde_cli
from seo_auditor.services.entregables_service import PERFILES_GENERACION
from seo_auditor.services.indexacion_service import ejecutar_indexacion
from seo_auditor.services.rendimiento_service import ejecutar_pagespeed_batch


def test_auditoria_request_contrato_por_defecto() -> None:
    """Valida campos y valores por defecto del contrato de entrada."""
    request = AuditoriaRequest(
        sitemap="https://ejemplo.com/sitemap.xml",
        periodo_desde="2026-03-01",
        periodo_hasta="2026-03-31",
        gestor="Gestor",
    )

    assert request.integraciones.usar_search_console is False
    assert request.cache.invalidar_antes_de_ejecutar is False
    assert request.informe.perfil_generacion == "auditoria-seo-completa"


def test_auditoria_result_contrato_minimo() -> None:
    """Valida construcción mínima del contrato de salida estable."""
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=0,
        resultados=[],
        cliente="Cliente",
        fecha_ejecucion="2026-04-01",
        gestor="Gestor",
    )

    result = AuditoriaResult(auditoria=auditoria)

    assert isinstance(result.entregables, ResultadoEntregables)
    assert isinstance(result.resumen_ejecucion, ResumenEjecucion)
    assert result.resumen_ejecucion.codigo_salida == 0


def test_servicio_indexacion_reenvia_timeout(monkeypatch) -> None:
    """Asegura que el wrapper de indexación preserve firma y argumentos."""
    capturado = {}

    def _fake(url_sitemap: str, timeout: int = 10):
        capturado["url"] = url_sitemap
        capturado["timeout"] = timeout
        return {"ok": True}

    monkeypatch.setattr("seo_auditor.services.indexacion_service.analizar_indexacion_rastreo", _fake)

    salida = ejecutar_indexacion("https://ejemplo.com/sitemap.xml", timeout=30)

    assert salida == {"ok": True}
    assert capturado == {"url": "https://ejemplo.com/sitemap.xml", "timeout": 30}


def test_servicio_rendimiento_batch_preserva_kwargs(monkeypatch) -> None:
    """Asegura que el wrapper de PageSpeed aplique kwargs a cada URL."""
    llamadas = []

    def _fake(**kwargs):
        llamadas.append(kwargs)
        return {"url": kwargs["url"], "ok": True}

    monkeypatch.setattr("seo_auditor.services.rendimiento_service.analizar_pagespeed_url", _fake)

    salida = ejecutar_pagespeed_batch(["https://a.com", "https://b.com"], api_key="k", estrategia="mobile")

    assert len(salida) == 2
    assert all(item["ok"] for item in salida)
    assert llamadas[0]["api_key"] == "k"
    assert llamadas[1]["estrategia"] == "mobile"


def test_construir_request_valida_entregables_por_perfil() -> None:
    """Valida entregables contractuales por perfil de generación."""
    args = SimpleNamespace(
        sitemap="https://ejemplo.com/sitemap.xml",
        output="./salidas",
        usar_ia=False,
        noGSC=False,
        cache_ttl=0,
        invalidar_cache=False,
        modo="entrega-completa",
        gestor="Gestor",
        cliente="",
        modo_rapido=False,
        max_muestras_ia=10,
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
    )
    config = SimpleNamespace(gsc_enabled=True, ga_enabled=True, pagespeed_api_key="")

    for perfil, entregables in PERFILES_GENERACION.items():
        esperados = set(entregables)
        request = construir_request_desde_cli(args, config, "gemini-2.5-flash", "2026-03-01", "2026-03-31", perfil)
        assert set(request.informe.entregables_solicitados) == esperados
