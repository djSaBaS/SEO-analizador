# Preparación de arquitectura para modo pro

## Objetivo
Dejar preparado el diseño para integrar futuras fuentes autenticadas sin acoplar lógica no implementada en el flujo actual.

## Contrato de fuentes
- Fuentes públicas activas actuales:
  - `sitemap`
  - `rastreo_tecnico`
  - `html`
  - `pagespeed`
  - `ia` (solo para narrativa, no para medición)
- Fuentes autenticadas futuras (no activas en esta versión):
  - `search_console`
  - `ga4`

## Reglas editoriales activas
- El informe narrativo solo puede usar `fuentes_activas`.
- Si una fuente no está activa, no puede aparecer como evidencia factual.
- Las recomendaciones deben declararse desde los datos realmente disponibles.

## Punto de extensión previsto
1. Crear módulo `sources/publicas/*` para proveedores abiertos.
2. Crear módulo `sources/autenticadas/*` para conectores OAuth/servicio.
3. Resolver `fuentes_activas` por ejecución y pasarlas a IA/reporting.
4. Mantener desacoplamiento entre capa de adquisición de datos y capa de render.
