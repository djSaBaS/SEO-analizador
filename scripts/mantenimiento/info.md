# scripts/mantenimiento/info.md

## Objetivo
Agrupar validadores y utilidades de mantenimiento continuo del entorno del proyecto.

## Archivos
- `validar_entorno.py`: valida que toda carpeta alcance la norma de `info.md`.

## Responsabilidades
- Detectar incumplimientos estructurales antes de integrar cambios.
- Facilitar automatización en CI para gobernanza documental.

## Dependencias internas
- Usa la estructura de carpetas del repositorio como fuente de validación.
- Responde a la política documentada en `README.md` y `docs/arquitectura/sistema_documental.md`.

## Flujo de uso
1. Ejecutar `python scripts/mantenimiento/validar_entorno.py`.
2. Revisar carpetas reportadas sin `info.md`.
3. Crear o actualizar archivos faltantes y repetir validación.

## Notas de mantenimiento
- Mantener lista de exclusiones acotada a carpetas técnicas/temporales.
- Evitar lógica dependiente de entorno externo para uso en CI.

## Mejoras futuras
- Añadir validación de plantilla mínima obligatoria dentro de cada `info.md`.
- Integrar salida con formato machine-readable para pipelines.
