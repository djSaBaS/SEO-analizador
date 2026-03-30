# Reexporta utilidades documentales compartidas para uso explícito por formato.

# Importa saneamiento editorial para textos exportables.
from .core import sanitizar_texto_editorial

# Importa saneamiento final por formato para salida de entrega.
from .core import sanitizar_texto_final_exportable

# Importa saneamiento seguro para contenido textual en PDF.
from .core import sanear_texto_para_pdf

# Importa utilidad para limpiar markdown IA residual.
from .core import limpiar_markdown_crudo

# Importa utilidad para reemplazar emojis conflictivos por etiquetas seguras.
from .core import reemplazar_emojis_problematicos

# Importa utilidad para bloquear placeholders residuales.
from .core import bloquear_placeholders_residuales

# Importa utilidades de sanitización de valores en celdas Excel.
from .core import sanitizar_valor_excel
