"""Wrappers de compatibilidad para capa de reporters.

Centraliza accesos legacy con una ruta de migración explícita.
"""

from seo_auditor.reporters import exportar_excel, exportar_html, exportar_json, exportar_markdown_ia, exportar_pdf, exportar_word

__all__ = [
    "exportar_json",
    "exportar_excel",
    "exportar_word",
    "exportar_pdf",
    "exportar_html",
    "exportar_markdown_ia",
]
