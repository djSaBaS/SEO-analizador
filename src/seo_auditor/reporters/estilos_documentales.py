# Módulo puente: reexporta estilos documentales desde la nueva ubicación.
from seo_auditor.documentacion.shared.estilos import ORDEN_SEVERIDAD as ORDEN_SEVERIDAD
from seo_auditor.documentacion.shared.estilos import PDF_HORIZONTAL_MARGIN_POINTS as PDF_HORIZONTAL_MARGIN_POINTS
from seo_auditor.documentacion.shared.estilos import calcular_col_widths_pdf as calcular_col_widths_pdf
from seo_auditor.documentacion.shared.estilos import color_pastel_severidad as color_pastel_severidad

# Define superficie pública histórica del módulo puente.
__all__ = [
    "ORDEN_SEVERIDAD",
    "PDF_HORIZONTAL_MARGIN_POINTS",
    "calcular_col_widths_pdf",
    "color_pastel_severidad",
]
