# agent.md

## 1. Propósito del proyecto
Este repositorio está diseñado para ser mantenido por desarrolladores humanos y por agentes de inteligencia artificial.

El objetivo es garantizar un desarrollo:

- Consistente
- Seguro
- Testeable
- Reproducible
- Fácil de mantener a largo plazo

### Principios irrenunciables (orden de prioridad)
1. Seguridad
2. Estabilidad
3. Claridad del código
4. Mantenibilidad
5. Automatización de calidad (CI + tests)

La seguridad nunca se negocia.

## 2. Idioma obligatorio
Todo el contenido del repositorio debe estar en español:

- Comentarios del código
- Documentación
- Mensajes de commit
- Archivos Markdown
- Mensajes de error personalizados (cuando apliquen)

La coherencia lingüística forma parte de la calidad del proyecto.

## 3. Tipo de proyecto
Este repositorio es exclusivamente de tipo:

- Python

No se permite mezclar lógicas backend en otros lenguajes dentro del mismo repositorio, salvo que exista una arquitectura formalmente documentada que lo justifique.

## 4. Normas generales de desarrollo
### 4.1 Claridad del código
- El código debe ser explícito y comprensible.
- Evitar abreviaturas crípticas y “magia” innecesaria.
- Prohibido introducir complejidad sin beneficio real.
- No eliminar código sin verificar su uso real y sin justificarlo.
- No aplicar refactors masivos sin un objetivo claro.
- El código debe poder entenderse dentro de seis meses sin explicaciones adicionales.

### 4.2 Comentarios obligatorios (línea a línea)
Todo el código debe estar comentado línea a línea:

- El comentario va en la línea anterior.
- No usar prefijos como “Comentario:”.
- El comentario debe explicar qué hace la línea o por qué existe.

Excepción:

- Líneas autoexplicativas dentro de bloques ya documentados (docstring + contexto).

### 4.3 Documentación profesional de funciones y clases
Todas las funciones, clases y métodos deben documentarse con docstrings profesionales.

Debe incluir:

- Descripción clara
- Parámetros (tipo y descripción)
- Retorno
- Excepciones relevantes (si aplica)
- Consideraciones de seguridad si aplica
- Ejemplos breves cuando sea útil

No se aceptan funciones sin docstring.

## 5. Seguridad (PRIORIDAD ABSOLUTA)
Nunca confiar en entradas externas.

Reglas obligatorias:

- Validar, normalizar y sanear entradas provenientes de argumentos de CLI, ficheros, red/APIs o inputs del usuario.
- Prohibido exponer secretos en logs, trazas o errores.
- Manejo controlado de excepciones.
- Principio de mínimo privilegio.

### 5.1 Ejecución de comandos y sistema
- Evitar eval/exec.
- Evitar subprocess con shell=True salvo caso excepcional documentado.
- Nunca construir comandos con entrada libre del usuario.
- Preferir listas de argumentos y allowlist de opciones.

### 5.2 Gestión de secretos
- Prohibido subir secretos al repositorio.
- Debe existir plantilla de configuración cuando aplique.
- Credenciales y tokens deben cargarse mediante variables de entorno o gestor seguro.
- Nunca pasar secretos por parámetros de línea de comandos.

## 6. Calidad de código (sin alertas)
- Sin imports muertos.
- Sin variables no usadas.
- Sin complejidad accidental.

## 7. Dependencias y entorno
Debe existir un listado de dependencias y documentarse en README.md:

- Cómo crear entorno virtual en Windows (CMD y PowerShell)
- Cómo crear entorno virtual en Linux
- Cómo instalar dependencias
- Cómo ejecutar el proyecto
- Cómo generar ejecutable (.exe) si aplica

Las dependencias deben ser mínimas, justificadas y actualizables.

## 8. Estructura y documentación viva
Estructura base:

- /src
- /tests
- /docs
- /scripts

Reglas:

- Cada carpeta de primer nivel debe contener info.md actualizado.
- Si se modifica contenido dentro de una carpeta, debe actualizarse su info.md.
- version.md debe actualizarse cuando haya cambios de código.

## 9. Testing obligatorio
- Tests unitarios para funciones y clases.
- Tests de regresión: cada bug corregido añade un test.
- Tests de integración cuando aplique.
- Los tests deben fallar con mensajes accionables.
- El CI debe bloquear merges si fallan tests.

## 10. RepoGuardian
RepoGuardian valida en cada Pull Request:

- No se suben secretos.
- Si cambia src/, deben cambiar tests/.
- Si cambia código, debe actualizarse version.md.
- Si cambia una carpeta, debe actualizarse su info.md.

RepoGuardian no sustituye revisión humana. Refuerza disciplina y consistencia.

## 11. Flujo de trabajo Git
- `main` debe estar estable.
- Ramas: `feature/*`, `fix/*`, `docs/*`, `refactor/*`, `test/*`, `chore/*`.
- Recomendado: Conventional Commits.
- No se hace merge directo a `main`.

## 12. Restricciones específicas para agentes IA
- No introducir dependencias nuevas sin justificación y verificación.
- No refactorizar masivamente sin necesidad.
- No eliminar código sin verificar uso y sin test de respaldo.
- Priorizar cambios pequeños, revisables y testeados.
- No cambiar arquitectura sin documentarlo en `/docs`.
- El agente debe actuar como desarrollador senior responsable.
