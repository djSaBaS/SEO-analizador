"""Fábrica compartida de adaptadores para AuditoriaService."""

# Importa utilidades de ruta para inferencias de cliente en rutas locales.
from pathlib import Path

# Importa funciones de análisis técnico desde la capa existente.
from seo_auditor.analyzer import auditar_urls

# Importa utilidades de caché reutilizadas por CLI y web.
from seo_auditor.cache import invalidar_cache

# Importa extracción de URLs del sitemap desde el núcleo actual.
from seo_auditor.fetcher import extraer_urls_sitemap

# Importa servicios de indexación para enriquecer resultados.
from seo_auditor.indexacion import analizar_indexacion_rastreo, generar_gestion_indexacion_inteligente

# Importa generación premium de GA4 para perfiles compuestos.
from seo_auditor.integrations.ga4.premium_service import generar_informe_ga4_premium

# Importa integración de datos GA4 para comportamiento y conversión.
from seo_auditor.integrations.ga4.service import cargar_datos_analytics

# Importa generación narrativa opcional con IA.
from seo_auditor.integrations.gemini.service import generar_resumen_ia

# Importa integración de Search Console para señales orgánicas.
from seo_auditor.integrations.gsc.service import cargar_datos_search_console

# Importa utilidades de PageSpeed para métricas de rendimiento.
from seo_auditor.integrations.pagespeed.service import analizar_pagespeed_url, detectar_home

# Importa exportadores contractuales para entregables SEO.
from seo_auditor.reporters import (
    exportar_excel,
    exportar_html,
    exportar_json,
    exportar_markdown_ia,
    exportar_pdf,
    exportar_word,
)

# Importa contratos de adaptación de la capa de servicios.
from seo_auditor.services.auditoria_service import AuditoriaAdapters

# Importa utilidades generales de validación y trazabilidad.
from seo_auditor.utils import (
    es_url_http_valida,
    fecha_ejecucion_iso,
    inferir_cliente_desde_slug,
    iterar_con_progreso,
    slug_dominio_desde_url,
)


# Ejecuta PageSpeed con ambas estrategias manteniendo contrato histórico.
def _ejecutar_pagespeed(
    urls: list[str],
    api_key: str,
    timeout: int,
    reintentos: int,
    cache_dir=None,
    cache_ttl_segundos: int = 0,
):
    """Ejecuta PageSpeed para mobile y desktop reutilizando integración existente."""

    # Inicializa la colección de resultados agregados de rendimiento.
    resultados = []

    # Recorre URLs con trazabilidad de progreso en consola.
    for url in iterar_con_progreso(urls, "PageSpeed", "URL"):
        # Evalúa ambas estrategias Lighthouse para cada URL.
        for estrategia in ["mobile", "desktop"]:
            # Añade el resultado de la consulta actual con caché opcional.
            resultados.append(
                analizar_pagespeed_url(
                    url,
                    api_key,
                    estrategia,
                    timeout,
                    reintentos,
                    cache_dir,
                    cache_ttl_segundos,
                )
            )

    # Devuelve todos los resultados generados para cálculo posterior.
    return resultados


# Resuelve un nombre de cliente robusto para el informe GA4 premium.
def _resolver_cliente_informe_ga4(cliente_cli: str | None, sitemap: str | None) -> str:
    """Resuelve el cliente priorizando dato explícito y fallback por sitemap."""

    # Prioriza el nombre de cliente recibido explícitamente.
    if (cliente_cli or "").strip():
        # Devuelve el nombre normalizado evitando espacios residuales.
        return (cliente_cli or "").strip()

    # Normaliza el sitemap de entrada para inferencias seguras.
    sitemap_normalizado = (sitemap or "").strip()

    # Intenta inferir cliente desde dominio cuando el sitemap es HTTP válido.
    if sitemap_normalizado and es_url_http_valida(sitemap_normalizado):
        # Devuelve una inferencia amigable de cliente a partir del slug.
        return inferir_cliente_desde_slug(slug_dominio_desde_url(sitemap_normalizado))

    # Intenta inferir cliente desde nombre de archivo cuando la entrada es local.
    if sitemap_normalizado:
        # Extrae el nombre base del archivo sin extensión.
        nombre = Path(sitemap_normalizado).stem.strip()

        # Devuelve un nombre legible para portada cuando existe valor.
        if nombre:
            # Reemplaza separadores por espacios y aplica formato título.
            return nombre.replace("_", " ").replace("-", " ").title()

    # Aplica fallback estable para no romper flujo premium.
    return "Cliente GA4"


# Construye los adaptadores estándar compartidos por CLI y web.
def crear_adaptadores_auditoria() -> AuditoriaAdapters:
    """Construye el conjunto de adaptadores oficiales para AuditoriaService."""

    # Devuelve una instancia de adaptadores con funciones del núcleo actual.
    return AuditoriaAdapters(
        # Inyecta extracción de URLs desde sitemap.
        extraer_urls_sitemap=extraer_urls_sitemap,
        # Inyecta auditoría técnica de URLs.
        auditar_urls=auditar_urls,
        # Inyecta análisis de indexación y rastreo.
        analizar_indexacion_rastreo=analizar_indexacion_rastreo,
        # Inyecta generación de gestión de indexación inteligente.
        generar_gestion_indexacion_inteligente=generar_gestion_indexacion_inteligente,
        # Inyecta carga de datos desde Search Console.
        cargar_datos_search_console=cargar_datos_search_console,
        # Inyecta carga de datos desde Google Analytics 4.
        cargar_datos_analytics=cargar_datos_analytics,
        # Inyecta generación de resumen IA opcional.
        generar_resumen_ia=generar_resumen_ia,
        # Inyecta generador del informe premium de GA4.
        generar_informe_ga4_premium=generar_informe_ga4_premium,
        # Inyecta detector de URL home para PageSpeed.
        detectar_home=detectar_home,
        # Inyecta invalidación de caché local.
        invalidar_cache=invalidar_cache,
        # Inyecta exportador JSON técnico.
        exportar_json=exportar_json,
        # Inyecta exportador Excel SEO.
        exportar_excel=exportar_excel,
        # Inyecta exportador Word SEO.
        exportar_word=exportar_word,
        # Inyecta exportador PDF SEO.
        exportar_pdf=exportar_pdf,
        # Inyecta exportador HTML SEO.
        exportar_html=exportar_html,
        # Inyecta exportador Markdown IA auxiliar.
        exportar_markdown_ia=exportar_markdown_ia,
        # Inyecta iterador con progreso para salida operativa.
        iterar_con_progreso=iterar_con_progreso,
        # Inyecta validador de URL HTTP para controles de entrada.
        es_url_http_valida=es_url_http_valida,
        # Inyecta resolvedor de fecha de ejecución ISO.
        fecha_ejecucion_iso=fecha_ejecucion_iso,
        # Inyecta generación de slug de dominio.
        slug_dominio_desde_url=slug_dominio_desde_url,
        # Inyecta inferencia de cliente desde slug.
        inferir_cliente_desde_slug=inferir_cliente_desde_slug,
        # Inyecta ejecutor integrado de PageSpeed.
        ejecutar_pagespeed=_ejecutar_pagespeed,
        # Inyecta resolvedor robusto de cliente para GA4.
        resolver_cliente_informe_ga4=_resolver_cliente_informe_ga4,
    )
