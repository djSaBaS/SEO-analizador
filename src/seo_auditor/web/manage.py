"""Punto de entrada para gestionar la capa web interna en Django."""

# Importa utilidades del sistema para variables de entorno y argumentos.
import os
import sys

# Importa Path para resolver la ruta `src` del repositorio.
from pathlib import Path


# Ejecuta comandos de administración de Django con configuración del proyecto web.
def main() -> None:
    """Configura el entorno Django y despacha comandos administrativos."""

    # Calcula la ruta absoluta a la carpeta `src` del repositorio.
    ruta_src = Path(__file__).resolve().parents[3]

    # Inserta `src` en el path si no está presente para imports del paquete.
    if str(ruta_src) not in sys.path:
        # Prioriza el código local del repositorio durante la ejecución.
        sys.path.insert(0, str(ruta_src))

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
