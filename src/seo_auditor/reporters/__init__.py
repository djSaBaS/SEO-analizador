# Importa símbolos públicos históricos del núcleo compartido.
from .core import *

# Importa helpers privados que forman parte del contrato histórico de pruebas.
from .core import _calcular_col_widths_pdf
from .core import _construir_bloques_narrativos
from .core import _construir_quick_wins
from .core import _renderizar_bloque_dashboard
from .core import _renderizar_tabla_pdf
from .core import _renderizar_tabla_word
from .core import _resolver_subtablas_pdf

# Importa exportadores desacoplados por formato para mantener responsabilidad clara.
from .exportador_excel import exportar_excel
from .exportador_html import exportar_html
from .exportador_json import exportar_json
from .exportador_markdown import exportar_markdown_ia
from .exportador_pdf import exportar_pdf
from .exportador_word import exportar_word
