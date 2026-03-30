# Reexporta constantes y helpers de estilo transversal para exportadores.

# Importa orden de severidad para tablas y narrativa.
from .core import ORDEN_SEVERIDAD

# Importa margen horizontal reutilizable para maquetación PDF.
from .core import PDF_HORIZONTAL_MARGIN_POINTS

# Importa función privada de color para exponer una API pública con nombre explícito.
from .core import _color_pastel_severidad

# Importa función privada de cálculo de anchos para exponer una API pública con nombre explícito.
from .core import _calcular_col_widths_pdf


# Expone color pastel de severidad como utilidad pública del módulo de estilos.
def color_pastel_severidad(severidad: str) -> str:
    """Devuelve el color pastel asociado a una severidad para estilos visuales."""

    # Reutiliza la implementación central para mantener consistencia.
    return _color_pastel_severidad(severidad)


# Expone cálculo de anchos de tabla como utilidad pública del módulo de estilos.
def calcular_col_widths_pdf(columnas: list[str], filas: list[list[object]], ancho_util: float) -> list[float]:
    """Calcula anchos de columnas PDF manteniendo el ancho útil total disponible."""

    # Reutiliza la implementación central para evitar duplicación de reglas.
    return _calcular_col_widths_pdf(columnas, filas, ancho_util)
