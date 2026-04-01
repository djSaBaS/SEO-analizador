"""Ensamblador de auditoría SEO.

Coordina analizadores especializados y devuelve el resultado final.
"""

from seo_auditor.analyzers.contenido_analyzer import enriquecer_contenido
from seo_auditor.analyzers.indexacion_analyzer import enriquecer_indexacion
from seo_auditor.analyzers.tecnico_analyzer import auditar_urls as auditar_urls_tecnico


def auditar_urls(
    sitemap: str,
    urls: list[str],
    timeout: int,
    cliente: str,
    fecha_ejecucion: str,
    gestor: str,
    max_workers: int = 6,
):
    """Orquesta la auditoría técnica + enriquecimientos transversales.

    Nota: `max_workers` se mantiene para compatibilidad futura aunque la
    implementación técnica actual no paraleliza internamente.
    """
    resultado = auditar_urls_tecnico(
        sitemap=sitemap,
        urls=urls,
        timeout=timeout,
        cliente=cliente,
        fecha_ejecucion=fecha_ejecucion,
        gestor=gestor,
    )
    resultado = enriquecer_contenido(resultado)
    resultado = enriquecer_indexacion(resultado)
    return resultado
