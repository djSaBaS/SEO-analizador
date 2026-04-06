# Reexporta constantes y utilidades de estilo transversal.
from seo_auditor.reporters.core import ORDEN_SEVERIDAD as ORDEN_SEVERIDAD
from seo_auditor.reporters.core import PDF_HORIZONTAL_MARGIN_POINTS as PDF_HORIZONTAL_MARGIN_POINTS
from seo_auditor.reporters.core import _calcular_col_widths_pdf, _color_pastel_severidad


def color_pastel_severidad(severidad: str) -> str:
    """Devuelve el color pastel asociado a una severidad."""
    return _color_pastel_severidad(severidad)


def calcular_col_widths_pdf(columnas: list[str], filas: list[list[object]], ancho_util: float) -> list[float]:
    """Calcula anchos de columnas PDF manteniendo el ancho útil total."""
    return _calcular_col_widths_pdf(columnas, filas, ancho_util)


# Define API pública estable para módulos puente y consumidores legacy.
__all__ = [
    "ORDEN_SEVERIDAD",
    "PDF_HORIZONTAL_MARGIN_POINTS",
    "calcular_col_widths_pdf",
    "color_pastel_severidad",
]
