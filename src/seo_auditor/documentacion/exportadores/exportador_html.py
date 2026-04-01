# Exportador modular documental por formato (delegación central).
from pathlib import Path

from seo_auditor.models import ResultadoAuditoria
from seo_auditor.services.informe_service import InformeService


def exportar_html(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Exporta HTML desde un modelo semántico único preparado por servicio."""
    from seo_auditor.reporters.core import exportar_html as _impl

    servicio_informe = InformeService()
    paquete_informe = servicio_informe.preparar_informe(resultado, configuracion=None, incluir_markdown_ia=False)
    return _impl(resultado, path_salida, modelo_semantico=paquete_informe["modelo_semantico"])
