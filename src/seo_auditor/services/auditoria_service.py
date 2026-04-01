"""Orquestador principal de auditoría SEO con contratos estables."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from seo_auditor.models import (
    AuditoriaRequest,
    AuditoriaResult,
    ConfiguracionCacheAuditoria,
    ConfiguracionInforme,
    FlagsIntegracionesAuditoria,
    ResultadoAuditoria,
    ResumenEjecucion,
    ResultadoEntregables,
    ResultadoRendimiento,
)
from seo_auditor.services.entregables_service import (
    ENTREGABLES_BASE_AUDITORIA,
    EntregablesAdapters,
    EntregablesService,
    ModeloEntregables,
    PERFILES_GENERACION,
)


@dataclass(slots=True)
class AuditoriaAdapters:
    """Dependencias inyectables para facilitar migración y compatibilidad."""
    extraer_urls_sitemap: Callable[..., list[str]]
    auditar_urls: Callable[..., Any]
    analizar_indexacion_rastreo: Callable[..., Any]
    generar_gestion_indexacion_inteligente: Callable[..., Any]
    cargar_datos_search_console: Callable[..., Any]
    cargar_datos_analytics: Callable[..., Any]
    generar_resumen_ia: Callable[..., str]
    generar_informe_ga4_premium: Callable[..., dict[str, Any]]
    detectar_home: Callable[..., str]
    invalidar_cache: Callable[..., int]
    exportar_json: Callable[..., Any]
    exportar_excel: Callable[..., Any]
    exportar_word: Callable[..., Any]
    exportar_pdf: Callable[..., Any]
    exportar_html: Callable[..., Any]
    exportar_markdown_ia: Callable[..., Any]
    iterar_con_progreso: Callable[..., Any]
    es_url_http_valida: Callable[[str], bool]
    fecha_ejecucion_iso: Callable[[], str]
    slug_dominio_desde_url: Callable[[str], str]
    inferir_cliente_desde_slug: Callable[[str], str]
    ejecutar_pagespeed: Callable[..., list[ResultadoRendimiento]]
    resolver_cliente_informe_ga4: Callable[[str | None, str | None], str]


class AuditoriaService:
    """Orquesta la ejecución completa de la auditoría y sus entregables."""

    def __init__(self, adapters: AuditoriaAdapters) -> None:
        self.adapters = adapters
        self.entregables_service = EntregablesService(
            EntregablesAdapters(
                exportar_json=adapters.exportar_json,
                exportar_excel=adapters.exportar_excel,
                exportar_word=adapters.exportar_word,
                exportar_pdf=adapters.exportar_pdf,
                exportar_html=adapters.exportar_html,
                exportar_markdown_ia=adapters.exportar_markdown_ia,
                generar_informe_ga4_premium=adapters.generar_informe_ga4_premium,
                iterar_con_progreso=adapters.iterar_con_progreso,
            )
        )

    def ejecutar(self, request: AuditoriaRequest) -> int:
        """Ejecuta la auditoría y devuelve el código de salida para la CLI."""
        resultado = self.ejecutar_contrato(request)
        return resultado.resumen_ejecucion.codigo_salida

    def ejecutar_contrato(self, request: AuditoriaRequest) -> AuditoriaResult:
        """Ejecuta la auditoría y devuelve el contrato estable entre servicios."""
        argumentos = request.argumentos
        configuracion = request.configuracion

        if argumentos and argumentos.testia:
            return self._resultado_solo_codigo(self._ejecutar_testia(configuracion, request.modelo_ia))
        if argumentos and argumentos.testgsc:
            return self._resultado_solo_codigo(self._ejecutar_testgsc(configuracion))
        if argumentos and argumentos.testga:
            return self._resultado_solo_codigo(self._ejecutar_testga(configuracion))
        if request.informe.perfil_generacion == "solo-ga4-premium":
            return self._resultado_solo_codigo(self._ejecutar_modo_ga4_premium(request))
        return self._ejecutar_auditoria_completa(request)

    def _resultado_solo_codigo(self, codigo: int) -> AuditoriaResult:
        """Crea un contrato mínimo para flujos de conectividad sin auditoría completa."""
        auditoria_vacia = ResultadoAuditoria(
            sitemap="",
            total_urls=0,
            resultados=[],
            cliente="",
            fecha_ejecucion="",
            gestor="",
        )
        return AuditoriaResult(auditoria=auditoria_vacia, resumen_ejecucion=ResumenEjecucion(codigo_salida=codigo))

    def _ejecutar_testia(self, configuracion: Any, modelo_ia: str) -> int:
        from seo_auditor.integrations.gemini.service import probar_conexion_ia

        print("[testia] Validando configuración de IA...")
        try:
            respuesta = probar_conexion_ia(configuracion.gemini_api_key, modelo_ia)
            print(f"[testia] OK. Modelo={modelo_ia}. Respuesta={respuesta}")
            return 0
        except Exception as exc:
            print(f"[testia] Error: {exc}")
            return 1

    def _ejecutar_testgsc(self, configuracion: Any) -> int:
        pistas = [(["no existe archivo de credenciales"], ["revisa GSC_CREDENTIALS_FILE; la ruta debe apuntar a un JSON de service account accesible."]), (["falta gsc_site_url"], ["define GSC_SITE_URL (ej.: sc-domain:midominio.com o https://www.midominio.com/)."]), (["insufficient", "forbidden", "403"], ["la service account no tiene permisos en la propiedad de Search Console."])]
        return self._ejecutar_prueba_conectividad("testgsc", "Google Search Console", configuracion, self.adapters.cargar_datos_search_console, "No se pudo validar la conexión con Search Console.", pistas, lambda datos: f"site_url={datos.site_url or configuracion.gsc_site_url} | periodo={datos.date_from}..{datos.date_to} | filas_paginas={len(datos.paginas)} | filas_queries={len(datos.queries)}")

    def _ejecutar_testga(self, configuracion: Any) -> int:
        pistas = [(["no existe archivo de credenciales"], ["revisa GA_CREDENTIALS_FILE; debe apuntar a un JSON de service account accesible."]), (["falta ga_property_id"], ["define GA_PROPERTY_ID con el identificador numérico de la propiedad GA4."]), (["ga_property_id debe ser numérico"], ["elimina prefijos como 'properties/' y deja solo dígitos (ej.: 123456789)."]), (["403", "sufficient permissions"], ["la service account no tiene acceso a la propiedad GA4.", "añade el email de la service account como Viewer/Analyst en Administrar acceso de la propiedad."])]
        return self._ejecutar_prueba_conectividad("testga", "Google Analytics 4", configuracion, self.adapters.cargar_datos_analytics, "No se pudo validar la conexión con Google Analytics 4.", pistas, lambda datos: f"property_id={datos.property_id or configuracion.ga_property_id} | periodo={datos.date_from}..{datos.date_to} | filas_paginas={len(datos.paginas)}")

    def _ejecutar_prueba_conectividad(self, nombre_modo: str, nombre_servicio: str, configuracion: Any, funcion_carga: Callable[[Any], Any], mensaje_error_defecto: str, pistas_error: list[tuple[list[str], list[str]]], formatear_exito: Callable[[Any], str]) -> int:
        print(f"[{nombre_modo}] Validando conexión con {nombre_servicio}...")
        try:
            datos = funcion_carga(configuracion)
        except Exception as exc:
            print(f"[{nombre_modo}] Error inesperado al conectar con {nombre_servicio}: {exc!r}")
            return 1
        if not datos.activo:
            error_original = (datos.error or "").strip()
            print(f"[{nombre_modo}] Error: {error_original or mensaje_error_defecto}")
            error_normalizado = error_original.lower()
            for patrones, pistas in pistas_error:
                if any(p in error_normalizado for p in patrones):
                    for pista in pistas:
                        print(f"[{nombre_modo}] Detalle: {pista}")
            return 1
        print(f"[{nombre_modo}] OK. {formatear_exito(datos)}")
        return 0

    def _ejecutar_modo_ga4_premium(self, request: AuditoriaRequest) -> int:
        argumentos = request.argumentos
        carpeta_base = Path(request.informe.carpeta_salida or "./salidas")
        cliente = self.adapters.resolver_cliente_informe_ga4(request.cliente, request.sitemap)
        carpeta_salida = carpeta_base / "ga4_premium" / self.adapters.fecha_ejecucion_iso()
        print("[GA4 Premium] Generando informe premium en HTML/PDF/Excel...")
        salida = self.adapters.generar_informe_ga4_premium(request.configuracion, carpeta_salida, cliente, request.gestor, request.periodo_desde, request.periodo_hasta, argumentos.comparar if argumentos else "periodo-anterior", argumentos.provincia if argumentos else "")
        if not salida.get("activo", False):
            print(f"[GA4 Premium] Aviso: {salida.get('error', 'No se pudo generar el informe.')}")
            return 0
        print(f"[GA4 Premium] HTML: {salida.get('html')}")
        print(f"[GA4 Premium] PDF: {salida.get('pdf')}")
        print(f"[GA4 Premium] Excel: {salida.get('excel')}")
        return 0

    def _ejecutar_auditoria_completa(self, request: AuditoriaRequest) -> AuditoriaResult:
        configuracion = request.configuracion
        informe = request.informe
        cache = request.cache

        fecha = self.adapters.fecha_ejecucion_iso()
        slug = self.adapters.slug_dominio_desde_url(request.sitemap)
        cliente = request.cliente or self.adapters.inferir_cliente_desde_slug(slug)
        carpeta_base = Path(informe.carpeta_salida or "./salidas")
        carpeta_cache = Path(cache.ruta_cache) if cache.ruta_cache else carpeta_base / ".cache"

        if cache.invalidar_antes_de_ejecutar:
            print(f"[cache] Entradas eliminadas: {self.adapters.invalidar_cache(carpeta_cache)}")

        carpeta_salida = carpeta_base / slug / fecha
        entregables_perfil = informe.entregables_solicitados or PERFILES_GENERACION.get(informe.perfil_generacion, ENTREGABLES_BASE_AUDITORIA)

        print(f"[perfil] Ejecutando perfil de generación: {informe.perfil_generacion}")
        print("[1/6] Extrayendo URLs del sitemap...")
        urls = self.adapters.extraer_urls_sitemap(request.sitemap, configuracion.http_timeout, configuracion.max_urls)
        if request.modo_rapido:
            urls = urls[: min(25, len(urls))]
        if not urls:
            print("Error: no se han encontrado URLs válidas en el sitemap indicado.")
            return self._resultado_solo_codigo(1)

        print(f"[2/6] Auditando {len(urls)} URLs...")
        resultado = self.adapters.auditar_urls(request.sitemap, urls, configuracion.http_timeout, cliente, fecha, request.gestor)
        resultado.periodo_date_from = request.periodo_desde
        resultado.periodo_date_to = request.periodo_hasta
        resultado.indexacion_rastreo = self.adapters.analizar_indexacion_rastreo(request.sitemap, urls, configuracion.http_timeout)
        resultado.gestion_indexacion = self.adapters.generar_gestion_indexacion_inteligente(resultado.resultados)

        self._ejecutar_fuentes(request, resultado, urls, carpeta_cache)
        resultado_entregables = self._exportar_entregables(request, resultado, carpeta_salida, fecha, entregables_perfil)

        resumen = ResumenEjecucion(
            codigo_salida=0,
            total_urls_analizadas=len(urls),
            fuentes_activas=list(resultado.fuentes_activas),
            fuentes_fallidas=list(resultado.fuentes_fallidas),
            cache_invalidada=cache.invalidar_antes_de_ejecutar,
        )
        return AuditoriaResult(auditoria=resultado, entregables=resultado_entregables, resumen_ejecucion=resumen)

    def _ejecutar_fuentes(self, request: AuditoriaRequest, resultado: Any, urls: list[str], carpeta_cache: Path) -> None:
        integraciones = request.integraciones
        configuracion = request.configuracion

        max_urls = request.max_pagepsi_urls if request.max_pagepsi_urls > 0 else configuracion.max_pagepsi_urls
        timeout = request.pagepsi_timeout if request.pagepsi_timeout > 0 else configuracion.pagespeed_timeout
        reintentos = request.pagepsi_reintentos if request.pagepsi_reintentos >= 0 else configuracion.pagespeed_reintentos
        cache_ttl = request.cache.ttl_segundos if request.cache.ttl_segundos > 0 else configuracion.cache_ttl_segundos

        if integraciones.usar_pagespeed and configuracion.pagespeed_api_key:
            urls_ps = self._resolver_urls_pagespeed(request, urls, max_urls)
            resultado.rendimiento = self.adapters.ejecutar_pagespeed(urls_ps, configuracion.pagespeed_api_key, timeout, reintentos, carpeta_cache / "pagespeed", cache_ttl)
            estado_pagespeed: dict[str, dict[str, str]] = {}
            for item in resultado.rendimiento:
                estado_pagespeed.setdefault(item.url, {})
                estado_pagespeed[item.url][item.estrategia] = item.error or "ok"
            resultado.pagespeed_estado = estado_pagespeed
            scores_validos = [item.performance_score for item in resultado.rendimiento if isinstance(item.performance_score, (int, float))]
            if scores_validos:
                resultado.score_rendimiento = round(sum(scores_validos) / len(scores_validos), 1)
                resultado.seo_score_global = round(
                    (float(resultado.score_tecnico or 0.0) * 0.4)
                    + (float(resultado.score_contenido or 0.0) * 0.4)
                    + (float(resultado.score_rendimiento or 0.0) * 0.2),
                    1,
                )
            hay_metricas_validas = any(
                (
                    item.performance_score is not None
                    or item.accessibility_score is not None
                    or item.best_practices_score is not None
                    or item.seo_score is not None
                    or item.lcp is not None
                    or item.cls is not None
                    or item.inp is not None
                    or item.fcp is not None
                    or item.tbt is not None
                    or item.speed_index is not None
                )
                and not item.error
                for item in resultado.rendimiento
            )
            if hay_metricas_validas:
                if "pagespeed" not in resultado.fuentes_activas:
                    resultado.fuentes_activas.append("pagespeed")
            elif "pagespeed" not in resultado.fuentes_fallidas:
                resultado.fuentes_fallidas.append("pagespeed")

        if integraciones.usar_search_console:
            try:
                datos = self.adapters.cargar_datos_search_console(configuracion)
                resultado.search_console = datos
                resultado.gestion_indexacion = self.adapters.generar_gestion_indexacion_inteligente(resultado.resultados, datos.paginas)
                if datos.activo and (datos.paginas or datos.queries):
                    if "search_console" not in resultado.fuentes_activas:
                        resultado.fuentes_activas.append("search_console")
                elif "search_console" not in resultado.fuentes_fallidas:
                    resultado.fuentes_fallidas.append("search_console")
            except Exception as exc:
                if "search_console" not in resultado.fuentes_fallidas:
                    resultado.fuentes_fallidas.append("search_console")
                print(f"Aviso: fallo no bloqueante en Search Console: {exc}")
        else:
            print("[3.5/6] Search Console omitido por contrato de ejecución.")

        if integraciones.usar_analytics:
            try:
                resultado.analytics = self.adapters.cargar_datos_analytics(configuracion)
                if resultado.analytics.activo and resultado.analytics.paginas:
                    if "analytics" not in resultado.fuentes_activas:
                        resultado.fuentes_activas.append("analytics")
                elif "analytics" not in resultado.fuentes_fallidas:
                    resultado.fuentes_fallidas.append("analytics")
            except Exception as exc:
                if "analytics" not in resultado.fuentes_fallidas:
                    resultado.fuentes_fallidas.append("analytics")
                print(f"Aviso: fallo no bloqueante en Analytics: {exc}")

        if integraciones.usar_ia:
            try:
                resultado.resumen_ia = self.adapters.generar_resumen_ia(resultado, configuracion.gemini_api_key, request.modelo_ia, request.max_muestras_ia, request.informe.modo if request.informe.modo in {"completo", "resumen", "quickwins", "gsc", "roadmap"} else "completo", carpeta_cache / "ia", cache_ttl)
                if "ia" not in resultado.fuentes_activas:
                    resultado.fuentes_activas.append("ia")
            except Exception as exc:
                resultado.resumen_ia = f"No se pudo generar el informe con IA: {exc}"

    def _exportar_entregables(self, request: AuditoriaRequest, resultado: Any, carpeta_salida: Path, fecha: str, entregables_perfil: list[str]) -> ResultadoEntregables:
        print("[5/6] Exportando entregables profesionales...")
        cliente_premium = self.adapters.resolver_cliente_informe_ga4(request.cliente, request.sitemap)
        modelo_documental = ModeloEntregables(
            carpeta_salida=carpeta_salida,
            fecha_ejecucion=fecha,
            entregables_solicitados=entregables_perfil,
            cliente=cliente_premium,
            gestor=request.gestor,
            periodo_desde=request.periodo_desde,
            periodo_hasta=request.periodo_hasta,
            comparacion_ga4=request.argumentos.comparar if request.argumentos else "periodo-anterior",
            provincia_ga4=request.argumentos.provincia if request.argumentos else "",
        )
        resumen = self.entregables_service.generar_entregables(resultado, modelo_documental, request.configuracion)
        print(f"[6/6] Auditoría completada. Ruta base de salida: {carpeta_salida.resolve()}")
        print(f"[6/6] Generados: {resumen.generados or ['ninguno']}")
        print(f"[6/6] Omitidos: {resumen.omitidos or ['ninguno']}")
        print(f"[6/6] Errores no fatales: {resumen.errores_no_fatales or ['ninguno']}")
        return resumen

    def _resolver_urls_pagespeed(self, request: AuditoriaRequest, urls_sitemap: list[str], max_urls: int) -> list[str]:
        if request.pagepsi_url:
            return [request.pagepsi_url]
        if request.pagepsi_list_path:
            urls_archivo = self._cargar_urls_desde_archivo(request.pagepsi_list_path)
            if not urls_archivo:
                print("Aviso: --pagepsi-list no contiene URLs válidas. Se analizará la HOME por defecto.")
                return [self.adapters.detectar_home(request.sitemap, urls_sitemap)]
            return urls_archivo[:max_urls]
        return [self.adapters.detectar_home(request.sitemap, urls_sitemap)]

    def _cargar_urls_desde_archivo(self, ruta_archivo: str) -> list[str]:
        ruta = Path(ruta_archivo)
        if not ruta.exists() or not ruta.is_file():
            raise ValueError(f"No existe el archivo indicado en --pagepsi-list: {ruta_archivo}")
        urls = []
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            candidata = linea.strip()
            if candidata and self.adapters.es_url_http_valida(candidata):
                urls.append(candidata)
        return list(dict.fromkeys(urls))


def construir_request_desde_cli(
    argumentos: Any,
    configuracion: Any,
    modelo_ia: str,
    periodo_desde: str,
    periodo_hasta: str,
    perfil_generacion: str,
) -> AuditoriaRequest:
    """Convierte argumentos de CLI en un contrato de dominio explícito."""
    integraciones = FlagsIntegracionesAuditoria(
        usar_search_console=configuracion.gsc_enabled and not argumentos.noGSC,
        usar_analytics=configuracion.ga_enabled,
        usar_pagespeed=bool(configuracion.pagespeed_api_key),
        usar_ia=bool(argumentos.usar_ia),
        usar_ga4_premium=perfil_generacion == "solo-ga4-premium",
    )
    cache = ConfiguracionCacheAuditoria(
        ruta_cache=str(Path(argumentos.output or "./salidas") / ".cache"),
        ttl_segundos=argumentos.cache_ttl,
        invalidar_antes_de_ejecutar=bool(argumentos.invalidar_cache),
    )
    informe = ConfiguracionInforme(
        perfil_generacion=perfil_generacion,
        modo=argumentos.modo,
        carpeta_salida=argumentos.output or "./salidas",
        entregables_solicitados=list(PERFILES_GENERACION.get(perfil_generacion, ENTREGABLES_BASE_AUDITORIA)),
    )
    return AuditoriaRequest(
        sitemap=argumentos.sitemap or "",
        periodo_desde=periodo_desde,
        periodo_hasta=periodo_hasta,
        gestor=argumentos.gestor,
        cliente=(argumentos.cliente or "").strip(),
        modelo_ia=modelo_ia,
        modo_rapido=bool(argumentos.modo_rapido),
        max_muestras_ia=argumentos.max_muestras_ia,
        pagepsi_url=(argumentos.pagepsi or "").strip(),
        pagepsi_list_path=(argumentos.pagepsi_list or "").strip(),
        max_pagepsi_urls=argumentos.max_pagepsi_urls,
        pagepsi_timeout=argumentos.pagepsi_timeout,
        pagepsi_reintentos=argumentos.pagepsi_reintentos,
        integraciones=integraciones,
        cache=cache,
        informe=informe,
        configuracion=configuracion,
        argumentos=argumentos,
    )


def ejecutar_auditoria(urls: list[str], timeout: int, max_workers: int):
    """Fachada legacy temporal para imports históricos de `services`."""

    from seo_auditor.core.assembler import auditar_urls

    return auditar_urls(urls=urls, timeout=timeout, max_workers=max_workers)
