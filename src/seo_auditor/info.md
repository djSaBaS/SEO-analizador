# src/seo_auditor/info.md

## Objetivo
Agrupar la lógica de dominio del auditor SEO: análisis, integraciones, orquestación y exportación de resultados.

## Archivos
- `cli.py`: entrada principal del CLI del paquete.
- `analyzer.py`: análisis técnico y de contenido por URL.
- `indexacion.py`: lógica de indexabilidad y rastreo.
- `models.py`: modelos de datos del dominio.
- `config.py`: configuración y variables de entorno.
- Subcarpetas especializadas: `analyzers/`, `services/`, `integrations/`, `documentacion/`, `reporters/`, `legacy/`, `cache/`, `utils/`, `fetchers/`.

## Responsabilidades
- Implementar reglas de negocio del producto.
- Orquestar fuentes externas (GSC, GA4, PageSpeed, Gemini).
- Construir salidas estructuradas para exportación documental.

## Dependencias internas
- Depende de `src/main.py` como punto de invocación de alto nivel.
- Expone funcionalidad consumida por pruebas en `tests/`.
- Usa recursos documentados en `docs/` y prompts en `prompts/`.

## Flujo de uso
1. El usuario invoca el CLI.
2. `cli.py` configura ejecución y servicios.
3. Se ejecutan análisis e integraciones.
4. Se generan exportables y resultados finales.

## Notas de mantenimiento
- Mantener coherencia de contratos entre submódulos y capas legacy.
- Reflejar cambios estructurales en `src/info.md` y documentación de arquitectura.

## Mejoras futuras
- Reducir gradualmente acoplamientos legacy.
- Reforzar validaciones de límites entre capa de dominio y capa documental.
