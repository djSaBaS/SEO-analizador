# Importa el tipo Path para manejar la ruta de salida final.
from pathlib import Path

# Importa el modelo de resultado completo de la auditoría.
from seo_auditor.models import ResultadoAuditoria

# Importa la implementación central reutilizable del exportador Excel.
from .core import exportar_excel as _exportar_excel_central


# Exporta el informe en Excel con dashboard y hojas de detalle.
def exportar_excel(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Delega la construcción del Excel en la implementación central compartida."""

    # Ejecuta el flujo central de creación de hojas, estilos, tablas y gráficos.
    return _exportar_excel_central(resultado, path_salida)
