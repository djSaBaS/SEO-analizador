import argparse
from datetime import date, timedelta

from seo_auditor.analyzer import auditar_urls
from seo_auditor.cache import invalidar_cache
from seo_auditor.config import cargar_configuracion
from seo_auditor.fetcher import extraer_urls_sitemap
from seo_auditor.indexacion import analizar_indexacion_rastreo, generar_gestion_indexacion_inteligente
from seo_auditor.integrations.ga4.premium_service import generar_informe_ga4_premium
from seo_auditor.integrations.ga4.service import cargar_datos_analytics
from seo_auditor.integrations.gemini.service import generar_resumen_ia
from seo_auditor.integrations.gsc.service import cargar_datos_search_console
from seo_auditor.integrations.pagespeed.service import analizar_pagespeed_url, detectar_home
from seo_auditor.reporters import exportar_excel, exportar_html, exportar_json, exportar_markdown_ia, exportar_pdf, exportar_word
from seo_auditor.services.auditoria_service import AuditoriaAdapters, AuditoriaRequest, AuditoriaService
from seo_auditor.utils import es_url_http_valida, fecha_ejecucion_iso, inferir_cliente_desde_slug, iterar_con_progreso, slug_dominio_desde_url

GESTOR_POR_DEFECTO = "Juan Antonio Sánchez Plaza"


def _parsear_fecha_cli(valor: str, parametro: str) -> date:
    try:
        return date.fromisoformat(valor)
    except ValueError as exc:
        raise ValueError(f"{parametro} debe tener formato YYYY-MM-DD.") from exc


def _resolver_periodo_analisis(argumentos: argparse.Namespace) -> tuple[str, str]:
    date_from_cli = argumentos.date_from.strip()
    date_to_cli = argumentos.date_to.strip()
    if bool(date_from_cli) != bool(date_to_cli):
        raise ValueError("Debes indicar ambos parámetros: --date-from y --date-to.")
    if date_from_cli:
        fecha_desde = _parsear_fecha_cli(date_from_cli, "--date-from")
        fecha_hasta = _parsear_fecha_cli(date_to_cli, "--date-to")
        if fecha_desde >= fecha_hasta:
            raise ValueError("--date-from debe ser anterior a --date-to.")
        return fecha_desde.isoformat(), fecha_hasta.isoformat()
    fecha_hasta = date.today() - timedelta(days=1)
    fecha_desde = fecha_hasta - timedelta(days=27)
    return fecha_desde.isoformat(), fecha_hasta.isoformat()


def _resolver_perfil_generacion(argumentos: argparse.Namespace) -> str:
    if argumentos.generar_todo:
        return "todo"
    if argumentos.modo == "informe-ga4":
        return "solo-ga4-premium"
    if argumentos.modo == "entrega-completa":
        return "todo"
    return "auditoria-seo-completa"


def _resolver_cliente_informe_ga4(cliente_cli: str | None, sitemap: str | None) -> str:
    if (cliente_cli or "").strip():
        return (cliente_cli or "").strip()
    sitemap_normalizado = (sitemap or "").strip()
    if sitemap_normalizado and es_url_http_valida(sitemap_normalizado):
        return inferir_cliente_desde_slug(slug_dominio_desde_url(sitemap_normalizado))
    if sitemap_normalizado:
        from pathlib import Path

        nombre = Path(sitemap_normalizado).stem.strip()
        if nombre:
            return nombre.replace("_", " ").replace("-", " ").title()
    return "Cliente GA4"


def _ejecutar_pagespeed(
    urls: list[str],
    api_key: str,
    timeout: int,
    reintentos: int,
    cache_dir=None,
    cache_ttl_segundos: int = 0,
):
    resultados = []
    for url in iterar_con_progreso(urls, "PageSpeed", "URL"):
        for estrategia in ["mobile", "desktop"]:
            resultados.append(analizar_pagespeed_url(url, api_key, estrategia, timeout, reintentos, cache_dir, cache_ttl_segundos))
    return resultados


def _crear_adaptadores_temporales() -> AuditoriaAdapters:
    return AuditoriaAdapters(
        extraer_urls_sitemap=extraer_urls_sitemap,
        auditar_urls=auditar_urls,
        analizar_indexacion_rastreo=analizar_indexacion_rastreo,
        generar_gestion_indexacion_inteligente=generar_gestion_indexacion_inteligente,
        cargar_datos_search_console=cargar_datos_search_console,
        cargar_datos_analytics=cargar_datos_analytics,
        generar_resumen_ia=generar_resumen_ia,
        generar_informe_ga4_premium=generar_informe_ga4_premium,
        detectar_home=detectar_home,
        analizar_pagespeed_url=analizar_pagespeed_url,
        invalidar_cache=invalidar_cache,
        exportar_json=exportar_json,
        exportar_excel=exportar_excel,
        exportar_word=exportar_word,
        exportar_pdf=exportar_pdf,
        exportar_html=exportar_html,
        exportar_markdown_ia=exportar_markdown_ia,
        iterar_con_progreso=iterar_con_progreso,
        es_url_http_valida=es_url_http_valida,
        fecha_ejecucion_iso=fecha_ejecucion_iso,
        slug_dominio_desde_url=slug_dominio_desde_url,
        inferir_cliente_desde_slug=inferir_cliente_desde_slug,
        ejecutar_pagespeed=_ejecutar_pagespeed,
        resolver_cliente_informe_ga4=_resolver_cliente_informe_ga4,
    )


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auditor SEO profesional desde sitemap con exportación de informes.")
    parser.add_argument("--sitemap", required=False, help="URL del sitemap XML a analizar.")
    parser.add_argument("--output", required=False, help="Carpeta raíz donde se guardarán los informes.")
    parser.add_argument("--usar-ia", action="store_true", help="Activa el enriquecimiento del informe con Gemini.")
    parser.add_argument("--testia", action="store_true", help="Valida conexión y modelo IA con una llamada mínima.")
    parser.add_argument("--testga", action="store_true", help="Valida conexión con Google Analytics 4 y finaliza.")
    parser.add_argument("--testgsc", action="store_true", help="Valida conexión con Google Search Console y finaliza.")
    parser.add_argument("--modelo-ia", default="", help="Sobrescribe temporalmente el modelo de IA para esta ejecución.")
    parser.add_argument("--modo", choices=["completo", "resumen", "quickwins", "gsc", "roadmap", "informe-ga4", "entrega-completa"], default="completo", help="Selecciona el modo de ejecución/prompt.")
    parser.add_argument("--generar-todo", action="store_true", help="Atajo de orquestación equivalente a --modo entrega-completa.")
    parser.add_argument("--pagepsi", default="", help="URL concreta a analizar con PageSpeed Insights.")
    parser.add_argument("--pagepsi-list", default="", help="Ruta a archivo con URLs para PageSpeed (una por línea).")
    parser.add_argument("--max-pagepsi-urls", type=int, default=0, help="Límite manual de URLs para PageSpeed (0 usa configuración).")
    parser.add_argument("--pagepsi-timeout", type=int, default=0, help="Timeout de PageSpeed en segundos (0 usa configuración).")
    parser.add_argument("--pagepsi-reintentos", type=int, default=-1, help="Reintentos de PageSpeed (valor negativo usa configuración).")
    parser.add_argument("--gestor", default=GESTOR_POR_DEFECTO, help="Nombre del gestor responsable del informe.")
    parser.add_argument("--cliente", default="", help="Nombre de cliente para portada de informe premium (opcional).")
    parser.add_argument("--max-muestras-ia", type=int, default=15, help="Número máximo de muestras agregadas para la IA.")
    parser.add_argument("--modo-rapido", action="store_true", help="Limita volumen de URLs para una auditoría rápida.")
    parser.add_argument("--cache-ttl", type=int, default=0, help="TTL de caché local en segundos (0 usa configuración).")
    parser.add_argument("--invalidar-cache", action="store_true", help="Elimina la caché local antes de iniciar la auditoría.")
    parser.add_argument("--noGSC", action="store_true", help="Desactiva Google Search Console para esta ejecución, aunque esté configurado.")
    parser.add_argument("--comparar", choices=["periodo-anterior", "anio-anterior"], default="periodo-anterior", help="Comparación temporal para informe GA4.")
    parser.add_argument("--provincia", default="", help="Provincia objetivo para detalle de ciudades en informe GA4 premium.")
    parser.add_argument("--date-from", default="", help="Fecha inicial del análisis (YYYY-MM-DD).")
    parser.add_argument("--date-to", default="", help="Fecha final del análisis (YYYY-MM-DD).")
    return parser


def main() -> int:
    parser = crear_parser()
    argumentos = parser.parse_args()
    configuracion = cargar_configuracion()

    if not (argumentos.testia or argumentos.testga or argumentos.testgsc or _resolver_perfil_generacion(argumentos) == "solo-ga4-premium") and not argumentos.sitemap:
        print("Error: --sitemap es obligatorio salvo en modo --testia, --testga o --testgsc.")
        return 1
    if argumentos.sitemap and not es_url_http_valida(argumentos.sitemap):
        print("Error: el parámetro --sitemap debe ser una URL HTTP o HTTPS válida.")
        return 1
    if argumentos.pagepsi and not es_url_http_valida(argumentos.pagepsi):
        print("Error: --pagepsi debe ser una URL HTTP o HTTPS válida.")
        return 1
    if argumentos.pagepsi and argumentos.pagepsi_list:
        print("Error: no se puede usar --pagepsi y --pagepsi-list al mismo tiempo.")
        return 1
    if argumentos.max_muestras_ia <= 0:
        print("Error: --max-muestras-ia debe ser un entero positivo.")
        return 1
    if argumentos.max_pagepsi_urls < 0:
        print("Error: --max-pagepsi-urls no puede ser negativo.")
        return 1
    if argumentos.pagepsi_timeout < 0:
        print("Error: --pagepsi-timeout no puede ser negativo.")
        return 1
    if argumentos.pagepsi_reintentos < -1:
        print("Error: --pagepsi-reintentos debe ser -1 o mayor.")
        return 1

    try:
        periodo_desde, periodo_hasta = _resolver_periodo_analisis(argumentos)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    configuracion.gsc_date_from = periodo_desde
    configuracion.gsc_date_to = periodo_hasta
    configuracion.ga_date_from = periodo_desde
    configuracion.ga_date_to = periodo_hasta

    modelo_ia = argumentos.modelo_ia.strip() or configuracion.gemini_model
    print(f"[cli] Modo={argumentos.modo} | generar_todo={'sí' if argumentos.generar_todo else 'no'}")

    request = AuditoriaRequest(
        argumentos=argumentos,
        configuracion=configuracion,
        modelo_ia=modelo_ia,
        periodo_desde=periodo_desde,
        periodo_hasta=periodo_hasta,
    )
    servicio = AuditoriaService(_crear_adaptadores_temporales())
    return servicio.ejecutar(request)
