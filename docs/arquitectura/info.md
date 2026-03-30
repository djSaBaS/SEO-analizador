# docs/arquitectura/info.md

## Objetivo
Documentar decisiones de arquitectura y flujos estructurales del sistema.

## Archivos
- `arquitectura_general.md`: vista general del diseño técnico.
- `flujo_datos.md`: recorrido de datos entre módulos.
- `sistema_documental.md`: norma de gobernanza de `info.md` por carpeta.

## Responsabilidades
- Servir como referencia de diseño para cambios de código.
- Mantener trazabilidad de reglas de estructura documental.

## Dependencias internas
- Complementa `README.md` con detalle técnico.
- Se alinea con la estructura real de `src/` y `tests/`.

## Flujo de uso
1. Consultar aquí antes de cambios estructurales.
2. Actualizar documentos de arquitectura cuando cambie el diseño.
3. Validar coherencia contra reglas de mantenimiento del repositorio.

## Notas de mantenimiento
- Evitar descripciones teóricas sin reflejo en implementación.
- Actualizar referencias cruzadas cuando se renombren rutas.

## Mejoras futuras
- Añadir diagramas de componentes y secuencia.
- Incluir matriz de decisiones arquitectónicas (ADR) resumida.
