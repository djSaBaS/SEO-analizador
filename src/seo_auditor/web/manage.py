"""Punto de entrada para gestionar la capa web interna en Django."""

# Importa utilidades del sistema para variables de entorno y argumentos.
import os
import sys

# Importa Path para resolver rutas del repositorio.
from pathlib import Path


# Resuelve de forma robusta la carpeta `src` del repositorio.
def _resolver_ruta_src() -> Path:
    """Calcula la ruta absoluta de `src` verificando que contenga `seo_auditor`."""

    # Calcula la ruta del archivo `manage.py` actual.
    ruta_actual = Path(__file__).resolve()

    # Recorre ancestros desde la carpeta actual hasta la raíz.
    for ancestro in ruta_actual.parents:
        # Define candidata directa al subdirectorio `src` del ancestro.
        candidata = ancestro / "src"

        # Verifica que exista la carpeta `src/seo_auditor` esperada.
        if (candidata / "seo_auditor").is_dir():
            # Devuelve la ruta válida de `src` encontrada.
            return candidata

    # Lanza error controlado cuando no se encuentra la estructura esperada.
    raise RuntimeError("No se pudo localizar la carpeta 'src' que contiene el paquete 'seo_auditor'.")


# Inserta `src` en `sys.path` para permitir imports del paquete principal.
def _asegurar_src_en_syspath() -> Path:
    """Añade la ruta `src` al `sys.path` cuando aún no está registrada."""

    # Resuelve la ruta robusta de la carpeta `src` del proyecto.
    ruta_src = _resolver_ruta_src()

    # Convierte la ruta a texto para comparación con `sys.path`.
    ruta_src_texto = str(ruta_src)

    # Inserta `src` en el path cuando todavía no existe.
    if ruta_src_texto not in sys.path:
        # Prioriza el código local del repositorio en importación.
        sys.path.insert(0, ruta_src_texto)

    # Devuelve la ruta insertada para trazabilidad en tests.
    return ruta_src


# Ejecuta comandos de administración de Django con configuración del proyecto web.
def main() -> None:
    """Configura el entorno Django y despacha comandos administrativos."""

    # Asegura que el paquete `seo_auditor` sea importable desde `src`.
    _asegurar_src_en_syspath()

    # Define el módulo de settings por defecto para esta capa web.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seo_auditor.web.config.settings")

    # Importa el ejecutor de comandos de Django de forma diferida.
    from django.core.management import execute_from_command_line

    # Ejecuta el comando solicitado por el usuario.
    execute_from_command_line(sys.argv)


# Permite ejecutar este archivo como script principal.
if __name__ == "__main__":
    # Invoca la rutina principal de administración.
    main()
