"""Servicios de indexación y rastreo."""

from seo_auditor.indexacion import analizar_indexacion_rastreo


def ejecutar_indexacion(url_sitemap: str, timeout: int = 10):
    return analizar_indexacion_rastreo(url_sitemap, timeout=timeout)
