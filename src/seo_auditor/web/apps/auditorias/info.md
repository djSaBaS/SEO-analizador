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

## Notas de mantenimiento
- La ejecución se lanza en segundo plano con `ThreadPoolExecutor`; si se evoluciona a producción, migrar a cola dedicada (Celery/RQ) manteniendo el mismo adaptador de servicios.
- El dashboard excluye `.cache` para evitar sobrecoste de lectura de archivos.

- La vista de detalle muestra prioridades/quick wins reales derivados del motor y refleja fuentes incompatibles por dominio para trazabilidad.

- La descarga de entregables valida que las rutas estén dentro de `./salidas` para prevenir path traversal.
- El dashboard limita profundidad y volumen de escaneo de archivos para proteger rendimiento.
