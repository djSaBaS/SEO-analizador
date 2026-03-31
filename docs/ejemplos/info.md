# docs/ejemplos

Ejemplos prácticos de uso del CLI y flujos operativos.

## Objetivo
- Proporcionar comandos de referencia listos para usar por modo de ejecución.

## Archivos
- `comandos_cli.md`: catálogo de comandos por escenario de ejecución.

## Responsabilidades
- Mantener ejemplos alineados con los flags y modos vigentes del CLI.
- Cubrir escenarios frecuentes (auditoría estándar, entrega compuesta, pruebas de conectividad e informe GA4).

## Dependencias internas
- `src/seo_auditor/cli.py`: contrato de argumentos y modos disponibles.
- `README.md` y `CLI.md`: documentación operativa principal para validar coherencia.

## Flujo de uso
1. Revisar `comandos_cli.md` para seleccionar el escenario operativo.
2. Adaptar dominio, fechas, rutas de salida y banderas opcionales según el caso.
3. Ejecutar el comando y contrastar resultado con los artefactos esperados descritos en `README.md`.

## Notas de mantenimiento
- Debe mantenerse sincronizado con flags y modos vigentes en `src/seo_auditor/cli.py`.
- Cuando cambien perfiles de generación, actualizar ejemplos en el mismo commit.

## Mejoras futuras
- Incorporar ejemplos por sistema operativo (Linux/macOS/Windows) cuando difieran rutas o comillas.
- Añadir ejemplos de depuración para fallos de conectividad en integraciones externas.
