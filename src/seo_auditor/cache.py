# Importa serialización JSON para persistencia ligera.
import json

# Importa hash estable para claves de caché.
import hashlib

# Importa utilidades de tiempo para TTL.
import time

# Importa Path para rutas de disco.
from pathlib import Path

# Importa tipos para mayor claridad.
from typing import Any


# Construye una clave corta y estable para almacenar entradas de caché.
def construir_clave_cache(prefijo: str, payload: dict[str, Any]) -> str:
    """
    Genera un hash SHA-256 estable para identificar una respuesta cacheada.
    """

    # Serializa el payload ordenado para obtener huella determinista.
    base = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    # Calcula hash hexadecimal con prefijo funcional.
    return f"{prefijo}_{hashlib.sha256(base.encode('utf-8')).hexdigest()}"


# Lee una entrada de caché desde disco validando TTL.
def leer_cache(path_cache: Path, clave: str, ttl_segundos: int) -> Any | None:
    """
    Devuelve el valor cacheado si existe y no ha expirado.
    """

    # Construye la ruta física del archivo cacheado.
    ruta = path_cache / f"{clave}.json"

    # Sale sin valor cuando el archivo no existe.
    if not ruta.exists():
        # Devuelve vacío para forzar llamada real.
        return None

    # Carga el contenido serializado de la entrada.
    contenido = json.loads(ruta.read_text(encoding="utf-8"))

    # Obtiene timestamp de creación de la entrada.
    creado_en = float(contenido.get("timestamp", 0.0))

    # Evalúa expiración de la entrada según TTL configurado.
    if ttl_segundos > 0 and (time.time() - creado_en) > ttl_segundos:
        # Devuelve vacío cuando la entrada ya expiró.
        return None

    # Devuelve el valor original almacenado en caché.
    return contenido.get("valor")


# Guarda una entrada de caché en disco de forma segura.
def escribir_cache(path_cache: Path, clave: str, valor: Any) -> None:
    """
    Persiste una respuesta serializable en formato JSON.
    """

    # Garantiza que la carpeta de caché exista.
    path_cache.mkdir(parents=True, exist_ok=True)

    # Construye la ruta física del archivo de caché.
    ruta = path_cache / f"{clave}.json"

    # Serializa y escribe entrada con timestamp para control de TTL.
    ruta.write_text(json.dumps({"timestamp": time.time(), "valor": valor}, ensure_ascii=False), encoding="utf-8")


# Limpia todo el contenido de una carpeta de caché.
def invalidar_cache(path_cache: Path) -> int:
    """
    Elimina archivos de caché y devuelve el total eliminado.
    """

    # Sale sin cambios cuando la carpeta no existe.
    if not path_cache.exists():
        # Indica que no se eliminaron archivos.
        return 0

    # Inicializa contador de archivos eliminados.
    eliminados = 0

    # Recorre cualquier archivo de caché de forma recursiva.
    for archivo in path_cache.rglob("*"):
        # Omite directorios para borrar solo archivos.
        if not archivo.is_file():
            # Continúa con el siguiente elemento.
            continue

        # Filtra únicamente ficheros JSON de caché (sin importar mayúsculas).
        if archivo.suffix.lower() != ".json":
            # Ignora archivos no cacheables.
            continue

        # Elimina archivo actual.
        archivo.unlink(missing_ok=True)

        # Incrementa contador acumulado.
        eliminados += 1

    # Devuelve total de entradas invalidadas.
    return eliminados
