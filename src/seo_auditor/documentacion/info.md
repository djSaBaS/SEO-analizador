# src/seo_auditor/documentacion

Nueva capa documental modular para organizar responsabilidades de reporting.

## Submódulos
- `modelo/`: acceso explícito al modelo semántico transversal del informe.
- `builders/`: composición de secciones, jerarquías y estructuras intermedias reutilizables.
- `shared/`: helpers y estilos transversales (sanitización y constantes visuales).
- `exportadores/`: puntos de entrada por formato que delegan en la implementación central compartida.

## Nota de transición
- `src/seo_auditor/reporters/` se mantiene como capa puente de compatibilidad para imports históricos.

## Estado de fase
- Fase 1 cerrada (2026-03-31): la capa documental modular se mantiene como destino principal de exportación y `reporters/` funciona como wrapper de compatibilidad.
- Contrato de salida equivalente preservado para JSON, Excel, Word, PDF, HTML y Markdown IA.
