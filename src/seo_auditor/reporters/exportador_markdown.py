# Módulo puente: reexporta exportar_markdown_ia desde documentacion/exportadores.
from pathlib import Path

from seo_auditor.models import ResultadoAuditoria
from seo_auditor.documentacion.exportadores.exportador_markdown import exportar_markdown_ia as _impl


def exportar_markdown_ia(resultado: ResultadoAuditoria, path_salida: Path):
    """Mantiene el contrato histórico delegando en la nueva ubicación modular."""
    return _impl(resultado, path_salida)
