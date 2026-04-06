# Importa el módulo núcleo para mantener compatibilidad pública histórica.
from . import core as _core

# Importa exportadores desacoplados por formato para mantener responsabilidad clara.
from .exportador_excel import exportar_excel as exportar_excel
from .exportador_html import exportar_html as exportar_html
from .exportador_json import exportar_json as exportar_json
from .exportador_markdown import exportar_markdown_ia as exportar_markdown_ia
from .exportador_pdf import exportar_pdf as exportar_pdf
from .exportador_word import exportar_word as exportar_word

# Define símbolos públicos del núcleo histórico sin usar wildcard import.
_SIMBOLOS_CORE_PUBLICOS = [nombre for nombre in dir(_core) if not nombre.startswith("_")]

# Reinyecta símbolos del núcleo para mantener API heredada en import raíz.
globals().update({nombre: getattr(_core, nombre) for nombre in _SIMBOLOS_CORE_PUBLICOS})

# Define exportaciones públicas explícitas y mantenibles.
__all__ = sorted(
    [
        *_SIMBOLOS_CORE_PUBLICOS,
        "exportar_excel",
        "exportar_html",
        "exportar_json",
        "exportar_markdown_ia",
        "exportar_pdf",
        "exportar_word",
    ]
)
