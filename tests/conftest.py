# Importa sys para registrar la ruta de código fuente en tiempo de test.
import sys

# Importa Path para calcular rutas absolutas de forma portable.
from pathlib import Path


# Calcula la ruta absoluta a la carpeta src del proyecto.
RUTA_SRC = Path(__file__).resolve().parents[1] / "src"

# Inserta la ruta de src al inicio del path de importación si aún no existe.
if str(RUTA_SRC) not in sys.path:
    # Prioriza el código local del proyecto durante la ejecución de tests.
    sys.path.insert(0, str(RUTA_SRC))
