# docs/info.md

Documentación funcional y de arquitectura del proyecto.

## Archivos
- `arquitectura.md`: arquitectura actual, flujo operativo y decisiones técnicas.
- `modo-pro-preparacion.md`: criterios para evolución de fuentes/autenticación y reglas editoriales de datos.

## Convenciones
- Esta carpeta describe diseño y operación; no sustituye la guía de uso CLI (`README.md` y `CLI.md`).
- Debe mantenerse sincronizada con cambios de comportamiento en `src/seo_auditor/cli.py` y exportadores.
- Debe documentar también perfiles compuestos de generación cuando cambien (`--generar-todo`, `--modo entrega-completa` y evolución de paquetes de entregables).
- Los cambios de arquitectura documental deben reflejar explícitamente la capa semántica común usada por DOCX/PDF/HTML y sus políticas editoriales (sanitización y compatibilidad tipográfica).
