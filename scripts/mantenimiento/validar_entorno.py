"""Valida que cada carpeta del repositorio incluya un archivo info.md."""

# Importa utilidades de sistema para recorrer directorios de forma eficiente.
import os

# Importa utilidades para manejo robusto de rutas.
from pathlib import Path

# Define directorios internos que no forman parte de la estructura documental del proyecto.
DIRECTORIOS_EXCLUIDOS = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
}


# Define nombres de carpetas que se excluyen por ser artefactos de ejecución.
PREFIJOS_EXCLUIDOS = (".",)


# Define el nombre obligatorio del archivo documental de carpeta.
NOMBRE_INFO = "info.md"


# Obtiene la raíz del proyecto a partir de la ubicación del script.
ROOT = Path(__file__).resolve().parents[2]


# Determina si un segmento de ruta debe ignorarse por política.
def segmento_ignorado(segmento: str) -> bool:
    """Indica si un nombre de carpeta está fuera del alcance documental."""

    # Descarta directorios internos y cachés definidos por configuración.
    if segmento in DIRECTORIOS_EXCLUIDOS:
        return True
    # Descarta directorios ocultos para evitar falsos positivos con tooling local.
    if segmento.startswith(PREFIJOS_EXCLUIDOS):
        return True
    # Mantiene el segmento dentro del alcance de validación.
    return False


# Determina si una carpeta debe ignorarse de la validación.
def carpeta_ignorada(carpeta: Path) -> bool:
    """Indica si la carpeta está fuera del alcance documental."""

    # Evalúa solo la ruta relativa al repositorio para no depender del entorno local.
    ruta_relativa = carpeta.relative_to(ROOT)
    # Recorre cada segmento relativo para detectar exclusiones por nombre exacto.
    for segmento in ruta_relativa.parts:
        # Omite la carpeta cuando algún segmento está excluido.
        if segmento_ignorado(segmento):
            return True
    # Mantiene la carpeta dentro de la validación.
    return False


# Construye el listado de carpetas que no tienen info.md obligatorio.
def encontrar_carpetas_sin_info(raiz: Path) -> list[Path]:
    """Devuelve carpetas sin archivo info.md dentro del alcance definido."""

    # Inicializa el contenedor de resultados.
    faltantes: list[Path] = []
    # Recorre recursivamente carpetas usando os.walk para evitar iterar archivos innecesarios.
    for carpeta_actual, directorios, _ in os.walk(raiz):
        # Convierte la ruta actual a Path para operaciones de alto nivel.
        carpeta = Path(carpeta_actual)
        # Excluye directorios in-place para podar el recorrido en profundidad.
        directorios[:] = [
            nombre_directorio for nombre_directorio in directorios if not segmento_ignorado(nombre_directorio)
        ]
        # Omite la raíz porque este control aplica a carpetas del proyecto, no al repositorio completo.
        if carpeta == raiz:
            continue
        # Omite carpetas excluidas por política de segmentos relativos.
        if carpeta_ignorada(carpeta):
            continue
        # Marca la carpeta cuando no existe su archivo info.md.
        if not (carpeta / NOMBRE_INFO).exists():
            faltantes.append(carpeta)
    # Devuelve la lista ordenada para salida determinista en CI.
    return sorted(faltantes)


# Ejecuta la validación para uso por CLI y CI.
def main() -> int:
    """Ejecuta la comprobación de estructura documental y retorna código de salida."""

    # Detecta carpetas que incumplen la norma documental.
    faltantes = encontrar_carpetas_sin_info(ROOT)
    # Finaliza correctamente cuando no hay incumplimientos.
    if not faltantes:
        print("✅ Validación OK: todas las carpetas tienen info.md")
        return 0

    # Muestra cabecera de error para facilitar lectura en CI.
    print("❌ Validación fallida: faltan archivos info.md en las siguientes carpetas:")
    # Enumera cada carpeta en formato relativo a la raíz del repositorio.
    for carpeta in faltantes:
        print(f" - {carpeta.relative_to(ROOT)}")
    # Retorna código no exitoso para bloquear pipelines.
    return 1


# Permite ejecutar el script como comando directo.
if __name__ == "__main__":
    # Propaga código de salida al sistema operativo.
    raise SystemExit(main())
