"""Compatibilidad legacy del cliente Gemini.

Este módulo mantiene la ruta de importación histórica `seo_auditor.gemini_client`
reexportando la implementación canónica ubicada en
`seo_auditor.integrations.gemini.service`.
"""

from seo_auditor.integrations.gemini.service import *  # noqa: F401,F403
