# services

Espacio modular para servicios de orquestación funcional en **seo_auditor**.

## Estado de fase
- Ajuste de estabilidad (2026-04-01): se restaura paridad funcional del flujo previo (fuentes activas/fallidas, métricas PageSpeed consolidadas y resumen de entregables) tras revisión de regresiones.
- Fase 3 en progreso (2026-04-01): `AuditoriaService` concentra la secuencia principal, mientras `cli.py` queda como capa de entrada/dispatch con adaptadores temporales de compatibilidad legacy.
- Fase 2 cerrada (2026-03-31): servicios divididos por dominio (`auditoria`, `entregables`, `rendimiento`, `indexacion`, `priorizacion`) y usados por la CLI estable.
- Se preserva degradación elegante y compatibilidad operativa durante la transición.

## Contratos entre servicios (2026-04-01)
- `auditoria_service.py` recibe `AuditoriaRequest` y produce `AuditoriaResult` mediante `ejecutar_contrato`.
- La construcción de entrada desde CLI se concentra en `construir_request_desde_cli`, evitando parámetros sueltos en orquestación.
- `priorizacion_service.py` prioriza con salida explicable (`score`, `motivos`, `componentes`) a partir de `AuditoriaResult`.
- `ResultadoEntregables` consolida exportaciones generadas/omitidas/errores no fatales para desacoplar reporting documental.
