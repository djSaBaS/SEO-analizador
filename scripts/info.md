# scripts/info.md

## Objetivo
Concentrar scripts operativos y de mantenimiento automatizado del repositorio.

## Archivos
- `mantenimiento/`: scripts de validación y tareas rutinarias.

## Responsabilidades
- Proveer comprobaciones repetibles para CI y uso local.
- Reducir validaciones manuales propensas a errores.

## Dependencias internas
- Puede depender de reglas documentadas en `README.md` y `docs/`.
- Da soporte al control de calidad del flujo de desarrollo.

## Flujo de uso
1. Ejecutar scripts desde la raíz del proyecto.
2. Revisar salida y corregir incumplimientos reportados.
3. Integrar estos scripts en pipelines cuando aplique.

## Notas de mantenimiento
- Mantener scripts idempotentes y sin efectos colaterales inesperados.
- Documentar cada script nuevo en este `info.md`.

## Mejoras futuras
- Agregar más validaciones de consistencia documental y técnica.
- Unificar comandos en un launcher único de mantenimiento.
