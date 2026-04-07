# tests/unit

Pruebas unitarias migradas en paralelo desde `tests/`.


## Estado de fase
- Fase 2 cerrada (2026-03-31): esta carpeta representa la ubicación canónica de pruebas unitarias durante la transición.
- Se añaden pruebas para `InformeService` y para validar que exportadores documentales consumen el servicio de composición semántica común.

- Incluye validaciones de coherencia de dominio y exclusión de fuentes incompatibles en `test_coherencia_fuentes_service.py` y contratos de `AuditoriaService`.
