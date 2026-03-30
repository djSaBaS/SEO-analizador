"""Ensamblador de auditoría SEO.

Coordina analizadores especializados y devuelve el resultado final.
"""

from seo_auditor.analyzers.contenido_analyzer import enriquecer_contenido
from seo_auditor.analyzers.indexacion_analyzer import enriquecer_indexacion
from seo_auditor.analyzers.tecnico_analyzer import auditar_urls as auditar_urls_tecnico


def auditar_urls(urls: list[str], timeout: int = 10, max_workers: int = 6):
    """Orquesta la auditoría técnica + enriquecimientos transversales."""
    resultado = auditar_urls_tecnico(urls=urls, timeout=timeout, max_workers=max_workers)
    resultado = enriquecer_contenido(resultado)
    resultado = enriquecer_indexacion(resultado)
    return resultado
