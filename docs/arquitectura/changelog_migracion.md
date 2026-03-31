# Changelog de migración arquitectónica

## 2026-03-31 — Cierre Fase 1 y Fase 2

### Módulos movidos
- Reporting modular consolidado en `src/seo_auditor/documentacion/{modelo,builders,shared,exportadores}`.
- Organización funcional consolidada en `src/seo_auditor/{integrations,analyzers,services}`.
- Suite de pruebas reorganizada en `tests/unit` y `tests/integration` como estructura principal.

### Compatibilidades mantenidas
- `src/seo_auditor/reporters/` conserva wrappers activos para imports históricos de exportación.
- Se mantienen rutas legacy de tests en `tests/` para evitar ruptura mientras finaliza la transición.
- CLI sin cambios de contrato público (flags, modos, artefactos y estructura de salida).

### Riesgos pendientes
- Mantener sincronización entre wrappers legacy y nuevas implementaciones para evitar deriva funcional.
- Retirar rutas legacy de tests solo cuando toda la cobertura y tooling dependan de la nueva estructura.
- Vigilar deuda técnica de duplicidad temporal en documentación y aliases de import.
