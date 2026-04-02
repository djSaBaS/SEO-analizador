# src/seo_auditor/web/config/info.md

## Objetivo
Centralizar configuración Django de la web interna.

## Archivos
- `settings.py`: configuración de apps, base de datos y plantillas.
- `urls.py`: rutas raíz.
- `wsgi.py`: punto de entrada WSGI.

## Notas
- Configuración pensada para entorno local interno.

## Notas de seguridad
- `DJANGO_SECRET_KEY` debe definirse explícitamente cuando `DJANGO_DEBUG=false`; en debug local se usa clave efímera no persistida.
