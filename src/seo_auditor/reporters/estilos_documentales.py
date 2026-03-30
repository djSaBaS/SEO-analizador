# Reexporta constantes y helpers de estilo transversal para exportadores.

# Importa orden de severidad para tablas y narrativa.
from .core import ORDEN_SEVERIDAD

# Importa margen horizontal reutilizable para maquetación PDF.
from .core import PDF_HORIZONTAL_MARGIN_POINTS

# Importa color pastel por severidad para componentes HTML.
from .core import _color_pastel_severidad

# Importa cálculo de anchos de tabla para evitar desbordes en PDF.
from .core import _calcular_col_widths_pdf
