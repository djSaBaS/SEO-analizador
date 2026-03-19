# Arquitectura del proyecto

## Resumen
El sistema sigue una arquitectura modular sencilla y mantenible.

1. El CLI recibe un sitemap y una carpeta de salida.
2. La configuración carga variables de entorno de forma segura.
3. El módulo `fetcher` descarga el sitemap y obtiene las URLs.
4. El módulo `analyzer` analiza cada página y detecta problemas.
5. El módulo `reporters` genera los artefactos finales.
6. El módulo `gemini_client` redacta una capa consultiva opcional.

## Principios aplicados
- Seguridad por defecto.
- Dependencias mínimas.
- Validación explícita de entradas.
- Trazabilidad del resultado técnico.
- Escalabilidad por módulos.

## Próximas ampliaciones recomendadas
- Soporte para `robots.txt` y `sitemap_index` con sitemaps anidados complejos.
- Extracción de canonicals, robots y hreflang con mayor profundidad.
- Análisis de enlazado interno.
- Integración con PageSpeed Insights.
- Modo batch para varios dominios.
