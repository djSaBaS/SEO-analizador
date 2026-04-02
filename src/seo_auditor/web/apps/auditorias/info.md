# src/seo_auditor/web/apps/auditorias/info.md

## Objetivo
Implementar pantallas y persistencia mínima de auditorías internas.

## Archivos
- `forms.py`: formulario de nueva auditoría.
- `models.py`: persistencia ligera de ejecuciones.
- `services_web.py`: adaptadores web hacia servicios del núcleo.
- `views.py`: dashboard, alta, detalle y descargas.
- `urls.py`: rutas de la app.
- `migrations/`: migraciones de esquema.

## Relación con otras carpetas
- Consume `src/seo_auditor/services/` y `src/seo_auditor/models.py`.
- Renderiza plantillas de `src/seo_auditor/web/templates/auditorias/`.
