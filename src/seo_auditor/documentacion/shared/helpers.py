# Reexporta utilidades documentales compartidas para todos los formatos.
from seo_auditor.reporters.core import bloquear_placeholders_residuales as bloquear_placeholders_residuales
from seo_auditor.reporters.core import limpiar_markdown_crudo as limpiar_markdown_crudo
from seo_auditor.reporters.core import reemplazar_emojis_problematicos as reemplazar_emojis_problematicos
from seo_auditor.reporters.core import sanear_texto_para_pdf as sanear_texto_para_pdf
from seo_auditor.reporters.core import sanitizar_texto_editorial as sanitizar_texto_editorial
from seo_auditor.reporters.core import sanitizar_texto_final_exportable as sanitizar_texto_final_exportable
from seo_auditor.reporters.core import sanitizar_valor_excel as sanitizar_valor_excel

# Define la API pública para compatibilidad entre capas documentales.
__all__ = [
    "bloquear_placeholders_residuales",
    "limpiar_markdown_crudo",
    "reemplazar_emojis_problematicos",
    "sanear_texto_para_pdf",
    "sanitizar_texto_editorial",
    "sanitizar_texto_final_exportable",
    "sanitizar_valor_excel",
]
