# Preparación de arquitectura para modo pro

## Objetivo
Definir una guía de evolución para ampliar fuentes de datos y capacidades de informe sin romper compatibilidad ni mezclar responsabilidades.

## Estado actual (implementado)

### Fuentes públicas
- `sitemap`
- `rastreo_tecnico`
- `html`
- `pagespeed`

### Fuentes autenticadas opcionales
- `search_console`
- `analytics` (GA4)

### Fuente de narrativa
- `ia` (Gemini), utilizada para redacción y priorización, no como fuente de medición primaria.

## Reglas editoriales vigentes
- El informe debe basarse en datos realmente disponibles durante la ejecución.
- Si una fuente no está activa o falla, se refleja en degradación controlada sin inventar evidencia.
- Las recomendaciones deben ser coherentes con `fuentes_activas` y métricas consolidadas.

## Ruta de evolución recomendada
1. Añadir nuevas fuentes como conectores desacoplados.
2. Mantener contratos de salida tipados en `models.py`.
3. Reutilizar validaciones y estrategias de fallback ya usadas en GSC/GA4/PageSpeed.
4. Conservar exportadores independientes de la capa de adquisición.

## Criterios de calidad para nuevas integraciones
- Validación temprana de configuración y credenciales.
- Tolerancia a errores de red/permisos con mensajes accionables.
- Cobertura de tests de conectividad, flujo CLI y reporting.
- Documentación de variables de entorno y ejemplos CLI en `README.md` y `CLI.md`.
