# Módulo puente: reexporta modelo semántico documental desde la nueva ubicación.
from seo_auditor.documentacion.builders.secciones import construir_jerarquia_visible as construir_jerarquia_visible
from seo_auditor.documentacion.builders.secciones import construir_secciones_desde_ia as construir_secciones_desde_ia
from seo_auditor.documentacion.modelo.modelo_documental import (
    construir_modelo_semantico_informe as construir_modelo_semantico_informe,
)

# Define superficie pública histórica del módulo puente.
__all__ = [
    "construir_jerarquia_visible",
    "construir_modelo_semantico_informe",
    "construir_secciones_desde_ia",
]
