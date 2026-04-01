"""Orquestador principal de auditoría SEO."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from seo_auditor.models import ResultadoRendimiento
from seo_auditor.services.entregables_service import (
    ENTREGABLES_BASE_AUDITORIA,
    ENTREGABLE_EXCEL_SEO,
    ENTREGABLE_GA4_PREMIUM,
    ENTREGABLE_HTML_SEO,
    ENTREGABLE_JSON_TECNICO,
    ENTREGABLE_MARKDOWN_IA,
    ENTREGABLE_PDF_SEO,
    ENTREGABLE_WORD_SEO,
    PERFILES_GENERACION,
)


@dataclass
class AuditoriaRequest:
    """Datos de entrada normalizados para la ejecución de auditoría."""

    argumentos: Any
    configuracion: Any
    modelo_ia: str
    periodo_desde: str
    periodo_hasta: str


@dataclass
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
    analizar_pagespeed_url: Callable[..., ResultadoRendimiento]
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

    def ejecutar(self, request: AuditoriaRequest) -> int:
        argumentos = request.argumentos
        configuracion = request.configuracion
        perfil_generacion = self._resolver_perfil_generacion(argumentos)

        if argumentos.testia:
            return self._ejecutar_testia(configuracion, request.modelo_ia)
        if argumentos.testgsc:
            return self._ejecutar_testgsc(configuracion)
        if argumentos.testga:
            return self._ejecutar_testga(configuracion)
        if perfil_generacion == "solo-ga4-premium":
            return self._ejecutar_modo_ga4_premium(request)
        return self._ejecutar_auditoria_completa(request, perfil_generacion)

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
        if not argumentos.output:
            print("Aviso: no se indicó --output, se usará ./salidas por compatibilidad.")
            argumentos.output = "./salidas"
        cliente = self.adapters.resolver_cliente_informe_ga4(argumentos.cliente, argumentos.sitemap)
        carpeta_salida = Path(argumentos.output) / "ga4_premium" / self.adapters.fecha_ejecucion_iso()
        print("[GA4 Premium] Generando informe premium en HTML/PDF/Excel...")
        salida = self.adapters.generar_informe_ga4_premium(request.configuracion, carpeta_salida, cliente, argumentos.gestor, request.periodo_desde, request.periodo_hasta, argumentos.comparar, argumentos.provincia)
        if not salida.get("activo", False):
            print(f"[GA4 Premium] Aviso: {salida.get('error', 'No se pudo generar el informe.')}")
            return 0
        print(f"[GA4 Premium] HTML: {salida.get('html')}")
        print(f"[GA4 Premium] PDF: {salida.get('pdf')}")
        print(f"[GA4 Premium] Excel: {salida.get('excel')}")
        return 0

    def _ejecutar_auditoria_completa(self, request: AuditoriaRequest, perfil_generacion: str) -> int:
        a, c = request.argumentos, request.configuracion
        if not a.output:
            print("Aviso: no se indicó --output, se usará ./salidas por compatibilidad.")
            a.output = "./salidas"
        fecha = self.adapters.fecha_ejecucion_iso()
        slug = self.adapters.slug_dominio_desde_url(a.sitemap)
        cliente = self.adapters.inferir_cliente_desde_slug(slug)
        carpeta_cache = Path(a.output) / ".cache"
        if a.invalidar_cache:
            print(f"[cache] Entradas eliminadas: {self.adapters.invalidar_cache(carpeta_cache)}")
        carpeta_salida = Path(a.output) / slug / fecha
        entregables_perfil = PERFILES_GENERACION.get(perfil_generacion, ENTREGABLES_BASE_AUDITORIA)
        print(f"[perfil] Ejecutando perfil de generación: {perfil_generacion}")
        print("[1/6] Extrayendo URLs del sitemap...")
        urls = self.adapters.extraer_urls_sitemap(a.sitemap, c.http_timeout, c.max_urls)
        if a.modo_rapido:
            urls = urls[: min(25, len(urls))]
        if not urls:
            print("Error: no se han encontrado URLs válidas en el sitemap indicado.")
            return 1
        print(f"[2/6] Auditando {len(urls)} URLs...")
        resultado = self.adapters.auditar_urls(a.sitemap, urls, c.http_timeout, cliente, fecha, a.gestor)
        resultado.periodo_date_from = request.periodo_desde
        resultado.periodo_date_to = request.periodo_hasta
        resultado.indexacion_rastreo = self.adapters.analizar_indexacion_rastreo(a.sitemap, urls, c.http_timeout)
        resultado.gestion_indexacion = self.adapters.generar_gestion_indexacion_inteligente(resultado.resultados)
        self._ejecutar_fuentes(request, resultado, urls, carpeta_cache)
        self._exportar_entregables(request, resultado, carpeta_salida, fecha, perfil_generacion, entregables_perfil)
        return 0

    def _ejecutar_fuentes(self, request: AuditoriaRequest, resultado: Any, urls: list[str], carpeta_cache: Path) -> None:
        a, c = request.argumentos, request.configuracion
        max_urls = a.max_pagepsi_urls if a.max_pagepsi_urls > 0 else c.max_pagepsi_urls
        timeout = a.pagepsi_timeout if a.pagepsi_timeout > 0 else c.pagespeed_timeout
        reint = a.pagepsi_reintentos if a.pagepsi_reintentos >= 0 else c.pagespeed_reintentos
        cache_ttl = a.cache_ttl if a.cache_ttl > 0 else c.cache_ttl_segundos
        if c.pagespeed_api_key:
            urls_ps = self._resolver_urls_pagespeed(a, a.sitemap, urls, max_urls)
            resultado.rendimiento = self.adapters.ejecutar_pagespeed(
                urls_ps,
                c.pagespeed_api_key,
                timeout,
                reint,
                carpeta_cache / "pagespeed",
                cache_ttl,
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
            else:
                if "pagespeed" not in resultado.fuentes_fallidas:
                    resultado.fuentes_fallidas.append("pagespeed")
        if (not a.noGSC) and c.gsc_enabled:
            try:
                datos = self.adapters.cargar_datos_search_console(c)
                resultado.search_console = datos
                resultado.gestion_indexacion = self.adapters.generar_gestion_indexacion_inteligente(resultado.resultados, datos.paginas)
            except Exception as exc:
                print(f"Aviso: fallo no bloqueante en Search Console: {exc}")
        if c.ga_enabled:
            try:
                resultado.analytics = self.adapters.cargar_datos_analytics(c)
            except Exception as exc:
                print(f"Aviso: fallo no bloqueante en Analytics: {exc}")
        if a.usar_ia:
            try:
                resultado.resumen_ia = self.adapters.generar_resumen_ia(resultado, c.gemini_api_key, request.modelo_ia, a.max_muestras_ia, a.modo if a.modo in {"completo", "resumen", "quickwins", "gsc", "roadmap"} else "completo", carpeta_cache / "ia", cache_ttl)
            except Exception as exc:
                resultado.resumen_ia = f"No se pudo generar el informe con IA: {exc}"

    def _exportar_entregables(self, request: AuditoriaRequest, resultado: Any, carpeta_salida: Path, fecha: str, perfil_generacion: str, entregables_perfil: list[str]) -> None:
        a, c = request.argumentos, request.configuracion
        print("[5/6] Exportando entregables profesionales...")
        exportadores = {
            ENTREGABLE_JSON_TECNICO: lambda: self.adapters.exportar_json(resultado, carpeta_salida),
            ENTREGABLE_EXCEL_SEO: lambda: self.adapters.exportar_excel(resultado, carpeta_salida),
            ENTREGABLE_WORD_SEO: lambda: self.adapters.exportar_word(resultado, carpeta_salida),
            ENTREGABLE_PDF_SEO: lambda: self.adapters.exportar_pdf(resultado, carpeta_salida),
            ENTREGABLE_HTML_SEO: lambda: self.adapters.exportar_html(resultado, carpeta_salida),
            ENTREGABLE_MARKDOWN_IA: lambda: self.adapters.exportar_markdown_ia(resultado, carpeta_salida),
        }
        for entregable in self.adapters.iterar_con_progreso(entregables_perfil, "Exportación", "archivo"):
            if entregable in exportadores:
                try:
                    exportadores[entregable]()
                except Exception as exc:
                    print(f"  - Aviso: no se pudo exportar {entregable}: {exc}")
                continue
            if entregable == ENTREGABLE_GA4_PREMIUM and c.ga_enabled:
                try:
                    self.adapters.generar_informe_ga4_premium(c, Path(a.output) / "ga4_premium" / fecha, self.adapters.resolver_cliente_informe_ga4(a.cliente, a.sitemap), a.gestor, request.periodo_desde, request.periodo_hasta, a.comparar, a.provincia)
                except Exception as exc:
                    print(f"  - Aviso: no se pudo exportar {entregable}: {exc}")
        print(f"[6/6] Auditoría completada. Ruta base de salida: {carpeta_salida.resolve()}")

    def _resolver_urls_pagespeed(self, argumentos: Any, sitemap: str, urls_sitemap: list[str], max_urls: int) -> list[str]:
        if argumentos.pagepsi:
            return [argumentos.pagepsi]
        if argumentos.pagepsi_list:
            urls_archivo = self._cargar_urls_desde_archivo(argumentos.pagepsi_list)
            if not urls_archivo:
                print("Aviso: --pagepsi-list no contiene URLs válidas. Se analizará la HOME por defecto.")
                return [self.adapters.detectar_home(sitemap, urls_sitemap)]
            return urls_archivo[:max_urls]
        return [self.adapters.detectar_home(sitemap, urls_sitemap)]

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

    def _ejecutar_pagespeed(self, urls: list[str], api_key: str, timeout: int, reintentos: int, cache_dir: Path | None = None, cache_ttl_segundos: int = 0) -> list[ResultadoRendimiento]:
        resultados: list[ResultadoRendimiento] = []
        for url in self.adapters.iterar_con_progreso(urls, "PageSpeed", "URL"):
            for estrategia in ["mobile", "desktop"]:
                resultados.append(self.adapters.analizar_pagespeed_url(url, api_key, estrategia, timeout, reintentos, cache_dir, cache_ttl_segundos))
        return resultados

    def _resolver_cliente_informe_ga4(self, cliente_cli: str | None, sitemap: str | None) -> str:
        if (cliente_cli or "").strip():
            return (cliente_cli or "").strip()
        sitemap_normalizado = (sitemap or "").strip()
        if sitemap_normalizado and self.adapters.es_url_http_valida(sitemap_normalizado):
            return self.adapters.inferir_cliente_desde_slug(self.adapters.slug_dominio_desde_url(sitemap_normalizado))
        if sitemap_normalizado:
            nombre = Path(sitemap_normalizado).stem.strip()
            if nombre:
                return nombre.replace("_", " ").replace("-", " ").title()
        return "Cliente GA4"

    def _resolver_perfil_generacion(self, argumentos: Any) -> str:
        if argumentos.generar_todo:
            return "todo"
        if argumentos.modo == "informe-ga4":
            return "solo-ga4-premium"
        if argumentos.modo == "entrega-completa":
            return "todo"
        return "auditoria-seo-completa"


def ejecutar_auditoria(urls: list[str], timeout: int, max_workers: int):
    """Fachada legacy temporal para imports históricos de `services`."""

    from seo_auditor.core.assembler import auditar_urls

    return auditar_urls(urls=urls, timeout=timeout, max_workers=max_workers)
