"""Valida que cada carpeta del repositorio incluya un archivo info.md."""

# Importa utilidades para recorrer el sistema de archivos.
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


# Determina si una carpeta debe ignorarse de la validación.
def carpeta_ignorada(carpeta: Path) -> bool:
    """Indica si la carpeta está fuera del alcance documental."""

    # Recorre cada segmento de la ruta para detectar exclusiones por nombre exacto.
    for segmento in carpeta.parts:
        # Descarta directorios internos y cachés.
        if segmento in DIRECTORIOS_EXCLUIDOS:
            return True
        # Descarta directorios ocultos.
        if segmento.startswith(PREFIJOS_EXCLUIDOS):
            return True
    # Mantiene la carpeta dentro de la validación.
    return False


# Construye el listado de carpetas que no tienen info.md obligatorio.
def encontrar_carpetas_sin_info(raiz: Path) -> list[Path]:
    """Devuelve carpetas sin archivo info.md dentro del alcance definido."""

    # Inicializa el contenedor de resultados.
    faltantes: list[Path] = []
    # Recorre recursivamente todas las carpetas desde la raíz.
    for carpeta in sorted([raiz] + [ruta for ruta in raiz.rglob("*") if ruta.is_dir()]):
        # Omite la raíz porque este control aplica a carpetas del proyecto, no al repositorio completo.
        if carpeta == raiz:
            continue
        # Omite carpetas excluidas por política.
        if carpeta_ignorada(carpeta):
            continue
        # Marca la carpeta cuando no existe su archivo info.md.
        if not (carpeta / NOMBRE_INFO).exists():
            faltantes.append(carpeta)
    # Devuelve la lista de carpetas no conformes.
    return faltantes


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
