# Prompt/info.md

## Objetivo
Mantener las plantillas históricas de prompts en formato legado (`Prompt/`) para compatibilidad con flujos anteriores.

## Archivos
- `consulta_ia_prompt.txt`: prompt auxiliar para consultas de IA.
- `gsc_oportunidades.txt`: plantilla de oportunidades basadas en Search Console.
- `informe_general.txt`: plantilla de informe general.
- `quick_wins.txt`: plantilla de acciones rápidas.
- `roadmap.txt`: plantilla de hoja de ruta.
- `resumen_ejecutivo.txt`: plantilla de resumen ejecutivo.

## Responsabilidades
- Preservar archivos de prompts usados por automatizaciones antiguas.
- Evitar romper integraciones que todavía referencian la ruta `Prompt/`.

## Dependencias internas
- Se relaciona con `prompts/`, que concentra la ruta canónica actual.
- Puede ser leído por herramientas internas que no han migrado a la ruta en minúsculas.

## Flujo de uso
1. Revisar si un consumidor sigue apuntando a `Prompt/`.
2. Sincronizar contenido con `prompts/` cuando se actualicen plantillas.
3. Planificar migración progresiva hacia la ruta canónica.

## Notas de mantenimiento
- Esta carpeta es temporal por compatibilidad.
- Cualquier cambio debe reflejarse también en `prompts/` para evitar divergencias.

## Mejoras futuras
- Eliminar la carpeta cuando no existan consumidores dependientes de la ruta legacy.
- Automatizar una verificación de paridad de contenido entre `Prompt/` y `prompts/`.
