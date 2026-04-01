# Prompt/info.md

## Objetivo
Mantener únicamente el prompt histórico único para compatibilidad temporal (`Prompt/consulta_ia_prompt.txt`).

## Archivos
- `consulta_ia_prompt.txt`: plantilla legacy usada como último fallback.

## Responsabilidades
- Evitar romper ejecuciones previas que todavía referencian la ruta `Prompt/`.
- Servir solo como compatibilidad transitoria mientras la ruta canónica es `prompts/`.

## Dependencias internas
- El consumo principal de plantillas vive en `prompts/`.
- Esta carpeta solo se consulta si no hay prompt resoluble en la ruta canónica.

## Mejoras futuras
- Eliminar esta carpeta cuando no existan consumidores dependientes del archivo legacy.
