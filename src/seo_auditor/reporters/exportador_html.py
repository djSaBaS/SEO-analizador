# Importa el tipo Path para generar la ruta del archivo HTML.
from pathlib import Path

# Importa el modelo de resultado completo de la auditoría.
from seo_auditor.models import ResultadoAuditoria

# Importa la implementación central reutilizable del exportador HTML.
from .core import exportar_html as _exportar_html_central


# Exporta el informe en formato HTML portable.
def exportar_html(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Delega la maquetación HTML en la implementación central compartida."""

    # Ejecuta el flujo central de cabecera, bloques ejecutivos y tablas técnicas.
    return _exportar_html_central(resultado, path_salida)
