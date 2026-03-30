# Integración con Gemini

## Convención de prompts (decisión vigente)

A partir de esta actualización, la ruta canónica de plantillas es:

- `prompts/` (minúsculas, consistente con convención snake_case del repositorio).

## Resolución de prompts en ejecución

El cargador de IA sigue este orden:

1. Prompt específico del modo dentro de `prompts/`.
2. Fallback al prompt principal `prompts/informe_general.txt`.
3. Compatibilidad temporal con legado en `Prompt/consulta_ia_prompt.txt`.

## Compatibilidad legacy temporal

Se mantiene solo el fallback de lectura de `Prompt/consulta_ia_prompt.txt` para no romper ejecuciones previas que aún dependan del prompt histórico único.

No se considera canónica la carpeta `Prompt/` para plantillas por modo.

## Modos soportados

- `completo` → `informe_general.txt`
- `resumen` → `resumen_ejecutivo.txt`
- `quickwins` → `quick_wins.txt`
- `gsc` → `gsc_oportunidades.txt`
- `roadmap` → `roadmap.txt`
