# Importa el tipo Path para resolver la ruta de escritura del DOCX.
from pathlib import Path

# Importa el modelo de resultado completo de la auditoría.
from seo_auditor.models import ResultadoAuditoria

# Importa la implementación central reutilizable del exportador Word.
from .core import exportar_word as _exportar_word_central


# Exporta el informe en formato Word para entrega editable.
def exportar_word(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Delega la maquetación DOCX en la implementación central compartida."""

    # Ejecuta el flujo central de portada, metadatos, secciones y anexo técnico.
    return _exportar_word_central(resultado, path_salida)
