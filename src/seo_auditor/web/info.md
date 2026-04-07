# src/seo_auditor/web/info.md

## Objetivo
Alojar la primera capa web interna (Django) del producto SEO reutilizando el núcleo de servicios existente.

## Archivos y carpetas
- `manage.py`: entrada de administración Django.
- `config/`: settings, URLs raíz y WSGI.
- `apps/`: aplicaciones funcionales de la web (auditorías).
- `templates/`: plantillas HTML.
- `static/`: recursos estáticos CSS.

## Relación con otras carpetas
- Consume contratos y servicios de `src/seo_auditor/services/`.
- Reutiliza modelos de dominio en `src/seo_auditor/models.py`.

## Notas de mantenimiento
- Mantener esta capa como adaptador de entrada (sin duplicar negocio).
- Priorizar compatibilidad con CLI y contratos `AuditoriaRequest/AuditoriaResult`.

- El arranque web depende de `manage.py` con bootstrap robusto de ruta `src` para garantizar imports de `seo_auditor` desde la raíz del repositorio.
