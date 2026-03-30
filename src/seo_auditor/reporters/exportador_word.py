# Módulo puente: reexporta exportar_word desde documentacion/exportadores.
from pathlib import Path

from seo_auditor.models import ResultadoAuditoria
from seo_auditor.documentacion.exportadores.exportador_word import exportar_word as _impl


def exportar_word(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Mantiene el contrato histórico delegando en la nueva ubicación modular."""
    return _impl(resultado, path_salida)
