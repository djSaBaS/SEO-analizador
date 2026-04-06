# Importa módulo técnico para reconstruir exportaciones legacy sin regresión.
from . import tecnico_analyzer as _tecnico_analyzer

# Reexporta enriquecedores de contenido/indexación como API explícita estable.
from .contenido_analyzer import enriquecer_contenido as enriquecer_contenido
from .indexacion_analyzer import enriquecer_indexacion as enriquecer_indexacion

# Reexporta símbolos técnicos históricos para compatibilidad hacia atrás.
from .tecnico_analyzer import *  # noqa: F401,F403

# Construye lista de símbolos técnicos públicos del módulo heredado.
_SIMBOLOS_TECNICOS_PUBLICOS = [
    nombre_simbolo
    for nombre_simbolo in dir(_tecnico_analyzer)
    if not nombre_simbolo.startswith("_")
]

# Publica API combinada manteniendo wildcard import legacy.
__all__ = [
    "enriquecer_contenido",
    "enriquecer_indexacion",
    *_SIMBOLOS_TECNICOS_PUBLICOS,
]
