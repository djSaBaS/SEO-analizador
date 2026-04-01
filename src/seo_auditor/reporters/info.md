# src/seo_auditor/reporters

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

## Estado de fase
- Fase 1 cerrada (2026-03-31): wrappers activos y obligatorios para mantener imports históricos durante la transición.
- Esta carpeta no debe introducir nuevas reglas de negocio; su responsabilidad es compatibilidad de API y delegación a `documentacion/`.
