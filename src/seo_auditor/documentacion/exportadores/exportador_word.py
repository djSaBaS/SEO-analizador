# Exportador modular documental por formato (delegación central).
from pathlib import Path

from seo_auditor.models import ResultadoAuditoria
from seo_auditor.reporters.core import exportar_word as _impl


def exportar_word(resultado: ResultadoAuditoria, path_salida: Path):
    """Delega la exportación en la implementación central compartida."""
    return _impl(resultado, path_salida)
