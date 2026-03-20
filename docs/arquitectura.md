# Arquitectura del proyecto

## Resumen
El sistema sigue una arquitectura modular evolutiva, con separación clara por capas:

1. `cli.py`: orquestación de flujo y validación de parámetros.
2. `config.py`: configuración de entorno y límites operativos.
3. `fetcher.py` + `analyzer.py`: extracción de URLs y auditoría técnica SEO.
4. `pagespeed.py`: auditoría de rendimiento (laboratorio + campo público).
5. `gemini_client.py`: narrativa IA opcional con control de tokens y fuentes activas.
6. `reporters.py`: render profesional a JSON/Excel/Word/PDF/HTML.
7. `cache.py`: capa de caché local para reducir latencia y coste de APIs externas.

## Flujo actual
1. Se carga configuración segura desde entorno.
2. Se extraen URLs del sitemap con límite defensivo.
3. Se audita SEO técnico por URL.
4. Se ejecuta PageSpeed:
   - por defecto solo en HOME
   - con `--pagepsi` solo URL indicada
   - con `--pagepsi-list` lista acotada por límite.
5. Se genera IA solo si `--usar-ia`.
6. Se exporta documentación final sin markdown crudo en DOCX/PDF.

## Preparación para futura API propia
- La orquestación de CLI mantiene separación respecto a dominio (`models.py` + `analyzer.py`).
- Los servicios externos (`pagespeed.py`, `gemini_client.py`) ya se consumen como funciones desacopladas.
- Los exportadores permanecen aislados en `reporters.py`, facilitando exponerlos luego como endpoints.
- La caché local se desacopla en `cache.py`, lista para migrar a Redis u otro backend en modo API.

## Decisiones técnicas clave
- Estructura intermedia IA→secciones para desacoplar texto libre de render final.
- Jerarquía documental fija para evitar duplicidades narrativas.
- Anexo técnico siempre construido desde datos estructurados.
- Fuentes activas explícitas en el resultado para evitar recomendaciones inventadas.
- Preparación de arquitectura para modo pro sin mezclar fuentes no implementadas.
