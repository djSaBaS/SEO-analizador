"""Pruebas de contratos del servicio de auditoría."""

from types import SimpleNamespace

from seo_auditor.models import (
    AuditoriaRequest,
    ConfiguracionCacheAuditoria,
    ConfiguracionInforme,
    FlagsIntegracionesAuditoria,
)
from seo_auditor.services.auditoria_service import AuditoriaAdapters, AuditoriaService


def _adaptadores_minimos() -> AuditoriaAdapters:
    """Construye adaptadores mínimos para validar rutas de control."""
    return AuditoriaAdapters(
        extraer_urls_sitemap=lambda *args, **kwargs: [],
        auditar_urls=lambda *args, **kwargs: None,
        analizar_indexacion_rastreo=lambda *args, **kwargs: {},
        generar_gestion_indexacion_inteligente=lambda *args, **kwargs: [],
        cargar_datos_search_console=lambda *args, **kwargs: None,
        cargar_datos_analytics=lambda *args, **kwargs: None,
        generar_resumen_ia=lambda *args, **kwargs: "",
        generar_informe_ga4_premium=lambda *args, **kwargs: {"activo": True, "html": "h", "pdf": "p", "excel": "e"},
        detectar_home=lambda *args, **kwargs: "https://ejemplo.com/",
        invalidar_cache=lambda *args, **kwargs: 0,
        exportar_json=lambda *args, **kwargs: None,
        exportar_excel=lambda *args, **kwargs: None,
        exportar_word=lambda *args, **kwargs: None,
        exportar_pdf=lambda *args, **kwargs: None,
        exportar_html=lambda *args, **kwargs: None,
        exportar_markdown_ia=lambda *args, **kwargs: None,
        iterar_con_progreso=lambda items, *args, **kwargs: items,
        es_url_http_valida=lambda _url: True,
        fecha_ejecucion_iso=lambda: "2026-04-01",
        slug_dominio_desde_url=lambda _url: "ejemplo",
        inferir_cliente_desde_slug=lambda _slug: "Cliente",
        ejecutar_pagespeed=lambda *args, **kwargs: [],
        resolver_cliente_informe_ga4=lambda cliente, sitemap: cliente or sitemap or "Cliente",
    )


def test_ejecutar_contrato_rutea_perfil_solo_ga4_premium_sin_flag() -> None:
    """Verifica que el perfil solo-ga4-premium no dependa del flag de integraciones."""
    servicio = AuditoriaService(_adaptadores_minimos())
    request = AuditoriaRequest(
        sitemap="https://ejemplo.com/sitemap.xml",
        periodo_desde="2026-03-01",
        periodo_hasta="2026-03-31",
        gestor="Gestor",
        integraciones=FlagsIntegracionesAuditoria(usar_ga4_premium=False),
        cache=ConfiguracionCacheAuditoria(),
        informe=ConfiguracionInforme(perfil_generacion="solo-ga4-premium", carpeta_salida="./salidas"),
        configuracion=SimpleNamespace(),
        argumentos=SimpleNamespace(
            comparar="periodo-anterior",
            provincia="",
            testia=False,
            testgsc=False,
            testga=False,
        ),
    )

    resultado = servicio.ejecutar_contrato(request)

    assert resultado.resumen_ejecucion.codigo_salida == 0
