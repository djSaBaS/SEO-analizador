# docs/integraciones

Documentación de integraciones externas disponibles en el proyecto.

## Objetivo
- Centralizar reglas de uso y mantenimiento de conectores externos (IA y fuentes autenticadas).

## Archivos
- `gemini.md`: integración IA (modelos, prompt y consideraciones de uso).

## Responsabilidades
- Definir contrato documental de cada integración (credenciales, flags, degradación y límites).
- Mantener coherencia entre la documentación técnica y el comportamiento real de la CLI.

## Dependencias internas
- `src/seo_auditor/integrations/`: implementación modular de conectores.
- `src/seo_auditor/cli.py`: activación por flags y modos de ejecución.
- `docs/arquitectura/`: decisiones de diseño y criterios de compatibilidad.

## Flujo de uso
1. Consultar la guía de la integración específica (por ejemplo `gemini.md`).
2. Configurar variables/credenciales requeridas en entorno.
3. Ejecutar CLI con los flags correspondientes y validar degradación elegante cuando aplique.

## Notas de mantenimiento
- Añadir aquí documentación equivalente cuando se amplíen conectores (GA4, GSC, PageSpeed, etc.).
- Cada nueva integración debe documentarse en el mismo commit que su incorporación técnica.

## Mejoras futuras
- Crear fichas homogéneas por integración (entrada/salida, errores frecuentes, checklist de diagnóstico).
- Incluir matriz comparativa de disponibilidad por modo CLI.
