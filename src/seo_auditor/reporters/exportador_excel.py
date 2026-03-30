# Módulo puente: reexporta exportar_excel desde documentacion/exportadores.
from pathlib import Path

from seo_auditor.models import ResultadoAuditoria
from seo_auditor.documentacion.exportadores.exportador_excel import exportar_excel as _impl


def exportar_excel(resultado: ResultadoAuditoria, path_salida: Path):
    """Mantiene el contrato histórico delegando en la nueva ubicación modular."""
    return _impl(resultado, path_salida)
