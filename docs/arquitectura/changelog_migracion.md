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

## 2026-04-01 — Cierre Fase 3 (contratos y orquestación)

### Módulos movidos
- Sin nuevos movimientos estructurales; se consolida la capa de contratos y pruebas sobre `services`.

### Compatibilidades mantenidas
- Equivalencia estructural verificada entre CLI histórica y `AuditoriaService`.
- Perfiles de generación mantenidos sin ruptura: `auditoria-seo-completa`, `todo`, `solo-ga4-premium`.
- Degradación elegante preservada para fallos o ausencia de GSC/GA4/PageSpeed/IA.

### Riesgos pendientes
- Reducir progresivamente duplicidad de pruebas legacy en `tests/` frente a canónicas de `tests/unit` y `tests/integration`.
- Seguir monitorizando deriva entre wrappers temporales de CLI y contratos de servicio.

### Criterios de cierre por fase
- **Fase 1:** paridad documental y exportadores estables.
- **Fase 2:** modularización funcional sin ruptura del contrato CLI.
- **Fase 3:** contratos tipados + equivalencia CLI/servicio + degradación elegante + perfiles de entregables verificados por tests.


## 2026-04-01 — Hardening de dependencias opcionales y fachada CLI

### Decisiones de fuente de verdad por capa
- **Oficial (nuevo):** `services/` orquesta casos de uso y define contratos de ejecución para CLI.
- **Oficial (nuevo):** `documentacion/` mantiene el modelo y exportadores canónicos para evolución futura.
- **Compatibilidad temporal:** `reporters/` y módulos raíz legacy (`analyzer.py`, `fetcher.py`, `indexacion.py`, etc.) se mantienen para no romper imports históricos.
- **Rutas provisionales explícitas:** wrappers/aliases legacy continúan hasta retirar dependencias externas de importación antigua.

### Cambios aplicados
- Integración Gemini convertida a **import perezoso** de `google.genai` para que la ausencia del SDK no rompa imports globales.
- CLI mantiene contrato estable y encapsula el wiring en `_crear_adaptadores_temporales` como paso transicional hacia una fachada más delgada.
- Se documenta que el acoplamiento legacy restante queda encapsulado en adaptadores de infraestructura, no en la interfaz CLI.

### Próximos pasos recomendados
- Migrar implementación interna de `documentacion/exportadores/*` para eliminar delegación residual a `reporters.core`.
- Retirar gradualmente wrappers de `reporters/` y módulos raíz legacy una vez que consumidores externos migren.
- Mantener pruebas de equivalencia mientras conviven ambos mundos, eliminando duplicidad al cerrar compatibilidad.
