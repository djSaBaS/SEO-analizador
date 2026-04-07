# Módulo puente: reexporta exportar_html desde documentacion/exportadores.
from pathlib import Path

from seo_auditor.documentacion.exportadores.exportador_html import exportar_html as _impl
from seo_auditor.models import ResultadoAuditoria


def exportar_html(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Mantiene el contrato histórico delegando en la nueva ubicación modular."""
    return _impl(resultado, path_salida)
