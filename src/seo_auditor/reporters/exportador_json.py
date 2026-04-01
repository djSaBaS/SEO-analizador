# Módulo puente: reexporta exportar_json desde documentacion/exportadores.
from pathlib import Path

from seo_auditor.models import ResultadoAuditoria
from seo_auditor.documentacion.exportadores.exportador_json import exportar_json as _impl


def exportar_json(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Mantiene el contrato histórico delegando en la nueva ubicación modular."""
    return _impl(resultado, path_salida)
