# Importa el tipo Path para manejar la ruta del markdown de revisión.
from pathlib import Path

# Importa el modelo de resultado completo de la auditoría.
from seo_auditor.models import ResultadoAuditoria

# Importa la implementación central reutilizable del exportador Markdown IA.
from .core import exportar_markdown_ia as _exportar_markdown_ia_central


# Exporta el markdown IA como artefacto editorial interno.
def exportar_markdown_ia(resultado: ResultadoAuditoria, path_salida: Path) -> Path | None:
    """Delega la exportación markdown IA en la implementación central compartida."""

    # Ejecuta el flujo central de normalización y escritura del markdown IA.
    return _exportar_markdown_ia_central(resultado, path_salida)
