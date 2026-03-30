"""Analizador específico de contenido.

En esta fase aplica enriquecimientos de hallazgos y métricas de contenido.
"""

from seo_auditor.models import ResultadoAuditoria


def enriquecer_contenido(resultado: ResultadoAuditoria) -> ResultadoAuditoria:
    """Punto de extensión para reglas de contenido transversales."""
    return resultado
