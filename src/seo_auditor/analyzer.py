"""Compatibilidad legacy para el analizador monolítico.

Deprecated: usar `seo_auditor.core.assembler` y `seo_auditor.analyzers.*`.
"""

from seo_auditor.analyzers import tecnico_analyzer as _tecnico
from seo_auditor.core.assembler import auditar_urls
from seo_auditor.analyzers.tecnico_analyzer import *  # noqa: F401,F403

# Reexport explícito de helpers privados usados por la suite histórica.
_calcular_metricas_contenido = _tecnico._calcular_metricas_contenido
_clasificar_canonical = _tecnico._clasificar_canonical
_es_redireccion_solo_slash = _tecnico._es_redireccion_solo_slash
_estructura_headings_correcta = _tecnico._estructura_headings_correcta
_normalizar_url_comparable = _tecnico._normalizar_url_comparable
