# Importa el tipo Path para la salida final del informe PDF.
from pathlib import Path

# Importa el modelo de resultado completo de la auditoría.
from seo_auditor.models import ResultadoAuditoria

# Importa la implementación central reutilizable del exportador PDF.
from .core import exportar_pdf as _exportar_pdf_central


# Exporta el informe en formato PDF portable.
def exportar_pdf(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Delega la maquetación PDF en la implementación central compartida."""

    # Ejecuta el flujo central de bloques semánticos y tablas narrativas del PDF.
    return _exportar_pdf_central(resultado, path_salida)
