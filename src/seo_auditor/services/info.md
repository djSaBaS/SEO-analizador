# services

Espacio modular para servicios de orquestación funcional en **seo_auditor**.

## Estado de fase
- Fase 3 en progreso (2026-04-01): `AuditoriaService` concentra la secuencia principal, mientras `cli.py` queda como capa de entrada/dispatch con adaptadores temporales de compatibilidad legacy.
- Fase 2 cerrada (2026-03-31): servicios divididos por dominio (`auditoria`, `entregables`, `rendimiento`, `indexacion`, `priorizacion`) y usados por la CLI estable.
- Se preserva degradación elegante y compatibilidad operativa durante la transición.
