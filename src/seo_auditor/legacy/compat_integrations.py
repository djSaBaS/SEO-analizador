"""Wrappers de compatibilidad para integraciones legacy."""

from seo_auditor.integrations.ga4.service import cargar_datos_analytics
from seo_auditor.integrations.ga4.premium_service import generar_informe_ga4_premium
from seo_auditor.integrations.gemini.service import generar_resumen_ia, probar_conexion_ia
from seo_auditor.integrations.gsc.service import cargar_datos_search_console
from seo_auditor.integrations.pagespeed.service import analizar_pagespeed_url, detectar_home

__all__ = [
    "generar_resumen_ia",
    "probar_conexion_ia",
    "cargar_datos_search_console",
    "cargar_datos_analytics",
    "generar_informe_ga4_premium",
    "analizar_pagespeed_url",
    "detectar_home",
]
