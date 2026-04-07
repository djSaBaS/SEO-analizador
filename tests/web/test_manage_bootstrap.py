# Importa sys para verificar y manipular el path de importación.
import sys

# Importa Path para validar rutas del repositorio.
from pathlib import Path

# Importa módulo manage de la capa web para probar bootstrap.
from seo_auditor.web import manage


# Verifica que el resolvedor localiza correctamente `src`.
def test_resolver_ruta_src_apunta_a_carpeta_valida():
    """Comprueba que `_resolver_ruta_src` devuelve la carpeta `src` del proyecto."""

    # Resuelve ruta de código fuente desde el helper de manage.
    ruta_src = manage._resolver_ruta_src()

    # Verifica que la carpeta `src` exista en disco.
    assert ruta_src.is_dir()

    # Verifica que dentro de `src` exista el paquete principal.
    assert (ruta_src / "seo_auditor").is_dir()


# Verifica que el helper inserta `src` en `sys.path` de forma idempotente.
def test_asegurar_src_en_syspath_inserta_ruta(monkeypatch):
    """Comprueba que `_asegurar_src_en_syspath` registra `src` para imports."""

    # Resuelve ruta esperada de `src` para comparación.
    ruta_src = manage._resolver_ruta_src()

    # Crea copia del path actual para restaurarlo tras la prueba.
    path_original = list(sys.path)

    # Filtra entradas iguales a `src` para simular estado sin bootstrap.
    path_filtrado = [entrada for entrada in path_original if Path(entrada).resolve() != ruta_src]

    # Sobrescribe `sys.path` temporal con el path filtrado.
    monkeypatch.setattr(sys, "path", path_filtrado)

    # Ejecuta helper que debe añadir `src` al inicio del path.
    ruta_insertada = manage._asegurar_src_en_syspath()

    # Verifica que la ruta devuelta coincide con `src` esperada.
    assert ruta_insertada == ruta_src

    # Verifica que la primera entrada del path corresponde a `src`.
    assert Path(sys.path[0]).resolve() == ruta_src
