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


def test_ejecutar_contrato_degradacion_integraciones_no_disponibles() -> None:
    """Verifica degradación elegante cuando GSC/GA4/PageSpeed/IA no están disponibles."""

    def _auditoria_minima(*_args, **_kwargs):
        from seo_auditor.models import ResultadoAuditoria

        return ResultadoAuditoria(
            sitemap="https://ejemplo.com/sitemap.xml",
            total_urls=1,
            resultados=[],
            cliente="Cliente",
            fecha_ejecucion="2026-04-01",
            gestor="Gestor",
        )

    adapters_base = _adaptadores_minimos()
    adapters = AuditoriaAdapters(
        extraer_urls_sitemap=lambda *_a, **_k: ["https://ejemplo.com/"],
        auditar_urls=_auditoria_minima,
        analizar_indexacion_rastreo=adapters_base.analizar_indexacion_rastreo,
        generar_gestion_indexacion_inteligente=adapters_base.generar_gestion_indexacion_inteligente,
        cargar_datos_search_console=lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("gsc off")),
        cargar_datos_analytics=lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("ga4 off")),
        generar_resumen_ia=lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("ia off")),
        generar_informe_ga4_premium=adapters_base.generar_informe_ga4_premium,
        detectar_home=adapters_base.detectar_home,
        invalidar_cache=adapters_base.invalidar_cache,
        exportar_json=adapters_base.exportar_json,
        exportar_excel=adapters_base.exportar_excel,
        exportar_word=adapters_base.exportar_word,
        exportar_pdf=adapters_base.exportar_pdf,
        exportar_html=adapters_base.exportar_html,
        exportar_markdown_ia=adapters_base.exportar_markdown_ia,
        iterar_con_progreso=adapters_base.iterar_con_progreso,
        es_url_http_valida=adapters_base.es_url_http_valida,
        fecha_ejecucion_iso=adapters_base.fecha_ejecucion_iso,
        slug_dominio_desde_url=adapters_base.slug_dominio_desde_url,
        inferir_cliente_desde_slug=adapters_base.inferir_cliente_desde_slug,
        ejecutar_pagespeed=lambda *_a, **_k: [],
        resolver_cliente_informe_ga4=adapters_base.resolver_cliente_informe_ga4,
    )

    servicio = AuditoriaService(adapters)
    request = AuditoriaRequest(
        sitemap="https://ejemplo.com/sitemap.xml",
        periodo_desde="2026-03-01",
        periodo_hasta="2026-03-31",
        gestor="Gestor",
        integraciones=FlagsIntegracionesAuditoria(
            usar_search_console=True,
            usar_analytics=True,
            usar_pagespeed=True,
            usar_ia=True,
        ),
        cache=ConfiguracionCacheAuditoria(),
        informe=ConfiguracionInforme(carpeta_salida="./salidas"),
        configuracion=SimpleNamespace(
            http_timeout=10,
            max_urls=10,
            pagespeed_api_key="dummy",
            max_pagepsi_urls=5,
            pagespeed_timeout=20,
            pagespeed_reintentos=1,
            cache_ttl_segundos=0,
            gemini_api_key="",
            ga_enabled=True,
            gsc_enabled=True,
        ),
        argumentos=SimpleNamespace(
            comparar="periodo-anterior", provincia="", testia=False, testgsc=False, testga=False
        ),
    )

    resultado = servicio.ejecutar_contrato(request)

    assert resultado.resumen_ejecucion.codigo_salida == 0
    assert "search_console" in resultado.auditoria.fuentes_fallidas
    assert "analytics" in resultado.auditoria.fuentes_fallidas
    assert "pagespeed" in resultado.auditoria.fuentes_fallidas
    assert "No se pudo generar el informe con IA" in resultado.auditoria.resumen_ia


def test_ejecutar_contrato_excluye_fuentes_incompatibles_por_dominio() -> None:
    """Verifica que GSC y GA4 se omitan cuando el dominio no coincide con el sitemap."""

    def _auditoria_minima(*_args, **_kwargs):
        from seo_auditor.models import ResultadoAuditoria

        return ResultadoAuditoria(
            sitemap="https://humanitaseducacion.com/sitemap.xml",
            total_urls=1,
            resultados=[],
            cliente="Cliente",
            fecha_ejecucion="2026-04-03",
            gestor="Gestor",
        )

    llamadas = {"gsc": 0, "ga": 0}
    adapters_base = _adaptadores_minimos()
    adapters = AuditoriaAdapters(
        extraer_urls_sitemap=lambda *_a, **_k: ["https://humanitaseducacion.com/"],
        auditar_urls=_auditoria_minima,
        analizar_indexacion_rastreo=adapters_base.analizar_indexacion_rastreo,
        generar_gestion_indexacion_inteligente=adapters_base.generar_gestion_indexacion_inteligente,
        cargar_datos_search_console=lambda *_a, **_k: llamadas.__setitem__("gsc", llamadas["gsc"] + 1),
        cargar_datos_analytics=lambda *_a, **_k: llamadas.__setitem__("ga", llamadas["ga"] + 1),
        generar_resumen_ia=lambda *_a, **_k: "",
        generar_informe_ga4_premium=adapters_base.generar_informe_ga4_premium,
        detectar_home=adapters_base.detectar_home,
        invalidar_cache=adapters_base.invalidar_cache,
        exportar_json=adapters_base.exportar_json,
        exportar_excel=adapters_base.exportar_excel,
        exportar_word=adapters_base.exportar_word,
        exportar_pdf=adapters_base.exportar_pdf,
        exportar_html=adapters_base.exportar_html,
        exportar_markdown_ia=adapters_base.exportar_markdown_ia,
        iterar_con_progreso=adapters_base.iterar_con_progreso,
        es_url_http_valida=adapters_base.es_url_http_valida,
        fecha_ejecucion_iso=adapters_base.fecha_ejecucion_iso,
        slug_dominio_desde_url=adapters_base.slug_dominio_desde_url,
        inferir_cliente_desde_slug=adapters_base.inferir_cliente_desde_slug,
        ejecutar_pagespeed=lambda *_a, **_k: [],
        resolver_cliente_informe_ga4=adapters_base.resolver_cliente_informe_ga4,
    )
    servicio = AuditoriaService(adapters)
    request = AuditoriaRequest(
        sitemap="https://humanitaseducacion.com/sitemap.xml",
        periodo_desde="2026-03-01",
        periodo_hasta="2026-03-31",
        gestor="Gestor",
        integraciones=FlagsIntegracionesAuditoria(
            usar_search_console=True,
            usar_analytics=True,
            usar_pagespeed=False,
            usar_ia=False,
        ),
        cache=ConfiguracionCacheAuditoria(),
        informe=ConfiguracionInforme(carpeta_salida="./salidas"),
        configuracion=SimpleNamespace(
            http_timeout=10,
            max_urls=10,
            pagespeed_api_key="",
            max_pagepsi_urls=5,
            pagespeed_timeout=20,
            pagespeed_reintentos=1,
            cache_ttl_segundos=0,
            gemini_api_key="",
            ga_enabled=True,
            gsc_enabled=True,
            gsc_site_url="sc-domain:colegiolegamar.com",
            ga_site_url="https://colegiolegamar.com/",
        ),
        argumentos=SimpleNamespace(
            comparar="periodo-anterior", provincia="", testia=False, testgsc=False, testga=False
        ),
    )

    resultado = servicio.ejecutar_contrato(request)

    assert llamadas["gsc"] == 0
    assert llamadas["ga"] == 0
    assert len(resultado.auditoria.fuentes_incompatibles) == 2
    assert len(resultado.resumen_ejecucion.fuentes_incompatibles) == 2


def test_ejecutar_contrato_omite_pagespeed_con_url_incompatible() -> None:
    """Verifica que PageSpeed no se ejecute si la URL manual es de otro dominio."""

    def _auditoria_minima(*_args, **_kwargs):
        from seo_auditor.models import ResultadoAuditoria

        return ResultadoAuditoria(
            sitemap="https://humanitaseducacion.com/sitemap.xml",
            total_urls=1,
            resultados=[],
            cliente="Cliente",
            fecha_ejecucion="2026-04-03",
            gestor="Gestor",
        )

    llamadas_pagespeed = {"total": 0}
    adapters_base = _adaptadores_minimos()
    adapters = AuditoriaAdapters(
        extraer_urls_sitemap=lambda *_a, **_k: ["https://humanitaseducacion.com/"],
        auditar_urls=_auditoria_minima,
        analizar_indexacion_rastreo=adapters_base.analizar_indexacion_rastreo,
        generar_gestion_indexacion_inteligente=adapters_base.generar_gestion_indexacion_inteligente,
        cargar_datos_search_console=adapters_base.cargar_datos_search_console,
        cargar_datos_analytics=adapters_base.cargar_datos_analytics,
        generar_resumen_ia=adapters_base.generar_resumen_ia,
        generar_informe_ga4_premium=adapters_base.generar_informe_ga4_premium,
        detectar_home=adapters_base.detectar_home,
        invalidar_cache=adapters_base.invalidar_cache,
        exportar_json=adapters_base.exportar_json,
        exportar_excel=adapters_base.exportar_excel,
        exportar_word=adapters_base.exportar_word,
        exportar_pdf=adapters_base.exportar_pdf,
        exportar_html=adapters_base.exportar_html,
        exportar_markdown_ia=adapters_base.exportar_markdown_ia,
        iterar_con_progreso=adapters_base.iterar_con_progreso,
        es_url_http_valida=adapters_base.es_url_http_valida,
        fecha_ejecucion_iso=adapters_base.fecha_ejecucion_iso,
        slug_dominio_desde_url=adapters_base.slug_dominio_desde_url,
        inferir_cliente_desde_slug=adapters_base.inferir_cliente_desde_slug,
        ejecutar_pagespeed=lambda *_a, **_k: llamadas_pagespeed.__setitem__("total", llamadas_pagespeed["total"] + 1),
        resolver_cliente_informe_ga4=adapters_base.resolver_cliente_informe_ga4,
    )
    servicio = AuditoriaService(adapters)
    request = AuditoriaRequest(
        sitemap="https://humanitaseducacion.com/sitemap.xml",
        periodo_desde="2026-03-01",
        periodo_hasta="2026-03-31",
        gestor="Gestor",
        pagepsi_url="https://colegiolegamar.com/",
        integraciones=FlagsIntegracionesAuditoria(
            usar_search_console=False,
            usar_analytics=False,
            usar_pagespeed=True,
            usar_ia=False,
        ),
        cache=ConfiguracionCacheAuditoria(),
        informe=ConfiguracionInforme(carpeta_salida="./salidas"),
        configuracion=SimpleNamespace(
            http_timeout=10,
            max_urls=10,
            pagespeed_api_key="dummy",
            max_pagepsi_urls=5,
            pagespeed_timeout=20,
            pagespeed_reintentos=1,
            cache_ttl_segundos=0,
            gemini_api_key="",
            ga_enabled=False,
            gsc_enabled=False,
        ),
        argumentos=SimpleNamespace(
            comparar="periodo-anterior", provincia="", testia=False, testgsc=False, testga=False
        ),
    )

    resultado = servicio.ejecutar_contrato(request)

    assert llamadas_pagespeed["total"] == 0
    assert any("pagespeed incompatible" in detalle for detalle in resultado.auditoria.fuentes_incompatibles)
