# Importa módulo de sistema para resolver el paquete cargado dinámicamente.
import sys

# Importa el tipo Path para resolver la ruta de escritura del DOCX.
from pathlib import Path

# Importa el modelo de resultado completo de la auditoría.
from seo_auditor.models import ResultadoAuditoria

# Importa el núcleo compartido donde vive la implementación real.
from . import core


# Exporta el informe en formato Word para entrega editable.
def exportar_word(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Delega la maquetación DOCX en la implementación central compartida."""

    # Recupera la fachada pública para respetar monkeypatch en tests.
    fachada_publica = sys.modules.get("seo_auditor.reporters")

    # Sincroniza el constructor del modelo semántico desde la fachada si fue parcheado.
    if fachada_publica is not None:
        core.construir_modelo_semantico_informe = getattr(
            fachada_publica,
            "construir_modelo_semantico_informe",
            core.construir_modelo_semantico_informe,
        )

    # Ejecuta el flujo central de portada, metadatos, secciones y anexo técnico.
    return core.exportar_word(resultado, path_salida)
