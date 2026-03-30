# prompts/info.md

## Objetivo
Centralizar las plantillas de prompts canónicas usadas por el flujo actual del auditor SEO.

## Archivos
- `gsc_oportunidades.txt`: prompt de oportunidades SEO desde GSC.
- `informe_general.txt`: prompt para informe consolidado.
- `quick_wins.txt`: prompt de recomendaciones de impacto rápido.
- `roadmap.txt`: prompt de plan de evolución.
- `resumen_ejecutivo.txt`: prompt de síntesis ejecutiva.

## Responsabilidades
- Mantener versiones oficiales de las plantillas de prompting.
- Servir como fuente principal para generación narrativa.

## Dependencias internas
- Es consumida por módulos del paquete `src/seo_auditor/` responsables de salida narrativa.
- Debe mantenerse alineada con la carpeta `Prompt/` mientras exista compatibilidad legacy.

## Flujo de uso
1. Editar aquí cualquier plantilla activa.
2. Validar que la plantilla produce salidas coherentes en pruebas o ejecución manual.
3. Sincronizar cambios en `Prompt/` mientras no se retire la compatibilidad.

## Notas de mantenimiento
- Evitar duplicidad de criterios entre archivos para facilitar mantenimiento.
- Documentar cambios relevantes en `version.md` cuando impacten comportamientos.

## Mejoras futuras
- Añadir versionado de prompts por caso de uso.
- Incorporar validaciones automáticas de placeholders esperados.
