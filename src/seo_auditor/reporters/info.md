# src/seo_auditor/reporters/info.md

Capa puente de compatibilidad para imports históricos de reporting SEO.

## Responsabilidades
- Mantener la API pública de `seo_auditor.reporters` sin ruptura durante la migración.
- Reexportar funciones/clases hacia `src/seo_auditor/documentacion/`.
- Conservar `core.py` como implementación común estable mientras avanza la extracción gradual.

## Nuevo mapa de responsabilidades
- `src/seo_auditor/documentacion/modelo/`: modelo semántico documental.
- `src/seo_auditor/documentacion/builders/`: composición de secciones y jerarquía.
- `src/seo_auditor/documentacion/shared/`: helpers/editorial/estilos transversales.
- `src/seo_auditor/documentacion/exportadores/`: entrypoints por formato.
