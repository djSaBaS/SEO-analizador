# Módulo puente: reexporta helpers documentales desde la nueva ubicación.
from seo_auditor.documentacion.shared.helpers import (
    bloquear_placeholders_residuales as bloquear_placeholders_residuales,
)
from seo_auditor.documentacion.shared.helpers import (
    limpiar_markdown_crudo as limpiar_markdown_crudo,
)
from seo_auditor.documentacion.shared.helpers import (
    reemplazar_emojis_problematicos as reemplazar_emojis_problematicos,
)
from seo_auditor.documentacion.shared.helpers import (
    sanear_texto_para_pdf as sanear_texto_para_pdf,
)
from seo_auditor.documentacion.shared.helpers import (
    sanitizar_texto_editorial as sanitizar_texto_editorial,
)
from seo_auditor.documentacion.shared.helpers import (
    sanitizar_texto_final_exportable as sanitizar_texto_final_exportable,
)
from seo_auditor.documentacion.shared.helpers import (
    sanitizar_valor_excel as sanitizar_valor_excel,
)

# Define superficie pública histórica del módulo puente.
__all__ = [
    "bloquear_placeholders_residuales",
    "limpiar_markdown_crudo",
    "reemplazar_emojis_problematicos",
    "sanear_texto_para_pdf",
    "sanitizar_texto_editorial",
    "sanitizar_texto_final_exportable",
    "sanitizar_valor_excel",
]
