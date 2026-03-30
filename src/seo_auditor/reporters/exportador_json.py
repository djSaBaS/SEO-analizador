# Importa el tipo Path para devolver la ruta del archivo generado.
from pathlib import Path

# Importa el modelo de resultado completo de la auditoría.
from seo_auditor.models import ResultadoAuditoria

# Importa la implementación central reutilizable del exportador JSON.
from .core import exportar_json as _exportar_json_central


# Exporta el informe técnico en JSON manteniendo el contrato histórico.
def exportar_json(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Delega la construcción JSON en la implementación central compartida."""

    # Ejecuta el flujo central de exportación JSON sin alterar comportamiento.
    return _exportar_json_central(resultado, path_salida)
