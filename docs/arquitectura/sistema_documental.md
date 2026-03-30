# Sistema documental de carpetas (`info.md`)

## Objetivo
Definir una norma única para que cada carpeta del repositorio tenga contexto funcional mínimo y mantenible.

## Regla obligatoria
- Toda carpeta nueva debe crearse junto con su `info.md` en el **mismo commit**.
- Si una carpeta existe sin `info.md`, el cambio debe añadirlo antes de fusionar.

## Plantilla mínima obligatoria
Cada `info.md` debe incluir, como mínimo, estas secciones:
1. `## Objetivo`
2. `## Archivos`
3. `## Responsabilidades`
4. `## Dependencias internas`
5. `## Flujo de uso`
6. `## Notas de mantenimiento`
7. `## Mejoras futuras`

## Alcance actual revisado
- `Prompt/` (compatibilidad legacy) con `info.md`.
- `prompts/` (ruta canónica) con `info.md`.
- Subcarpetas de `src/seo_auditor/` con `info.md`.
- `tests/fixtures/` deberá incluir `info.md` cuando se cree.

## Validación automática
La validación estructural se ejecuta con:

```bash
python scripts/mantenimiento/validar_entorno.py
```

El script falla (`exit 1`) si encuentra carpetas sin `info.md`.

## Mantenimiento
- Mantener sincronizado `info.md` cuando cambie el contenido de su carpeta.
- Actualizar este documento y `README.md` cuando cambie la política documental.
