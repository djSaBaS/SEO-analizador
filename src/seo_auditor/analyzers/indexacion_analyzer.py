"""Analizador específico de indexación.

En esta fase aplica reglas globales de indexación sobre el resultado agregado.
"""

from seo_auditor.models import ResultadoAuditoria


def enriquecer_indexacion(resultado: ResultadoAuditoria) -> ResultadoAuditoria:
    """Punto de extensión para reglas de indexación transversales."""
    return resultado
