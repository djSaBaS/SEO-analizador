# Módulo puente: reexporta exportar_pdf desde documentacion/exportadores.
from pathlib import Path

from seo_auditor.documentacion.exportadores.exportador_pdf import exportar_pdf as _impl
from seo_auditor.models import ResultadoAuditoria


def exportar_pdf(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Mantiene el contrato histórico delegando en la nueva ubicación modular."""
    return _impl(resultado, path_salida)
