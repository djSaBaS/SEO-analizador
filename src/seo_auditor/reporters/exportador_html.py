# Importa módulo de sistema para resolver el paquete cargado dinámicamente.
import sys

# Importa el tipo Path para generar la ruta del archivo HTML.
from pathlib import Path

# Importa el modelo de resultado completo de la auditoría.
from seo_auditor.models import ResultadoAuditoria

# Importa el núcleo compartido donde vive la implementación real.
from . import core


# Exporta el informe en formato HTML portable.
def exportar_html(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Delega la maquetación HTML en la implementación central compartida."""

    # Recupera la fachada pública para respetar monkeypatch en tests.
    fachada_publica = sys.modules.get("seo_auditor.reporters")

    # Sincroniza el constructor del modelo semántico desde la fachada si fue parcheado.
    if fachada_publica is not None:
        core.construir_modelo_semantico_informe = getattr(
            fachada_publica,
            "construir_modelo_semantico_informe",
            core.construir_modelo_semantico_informe,
        )

    # Ejecuta el flujo central de cabecera, bloques ejecutivos y tablas técnicas.
    return core.exportar_html(resultado, path_salida)
