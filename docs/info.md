# docs/info.md

Documentación viva del proyecto.

## Contenido
- `arquitectura.md`: visión general, flujo y decisiones técnicas.
- `modo-pro-preparacion.md`: diseño de separación entre fuentes públicas y fuentes autenticadas para evolución futura.

## Estado actual relevante
- La capa CLI ya soporta modo rápido, caché local con TTL e invalidación.
- La capa de exportadores incluye HTML reutilizable además de JSON/Excel/Word/PDF/Markdown IA.
- La lógica de canonical aplica normalización robusta para reducir falsos positivos por slash final.
