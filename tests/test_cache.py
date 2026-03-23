# Importa Path para crear estructura de directorios temporal.
from pathlib import Path

# Importa utilidades de caché bajo prueba.
from seo_auditor.cache import escribir_cache, invalidar_cache


# Verifica que la invalidación elimine caché en subcarpetas.
def test_invalidar_cache_elimina_archivos_recursivos(tmp_path: Path) -> None:
    """Comprueba que la invalidación borre entradas JSON de forma recursiva."""

    # Define carpeta raíz de caché.
    raiz_cache = tmp_path / ".cache"

    # Crea y escribe entrada en subcarpeta de IA.
    escribir_cache(raiz_cache / "ia", "clave_ia", {"valor": 1})

    # Crea y escribe entrada en subcarpeta de PageSpeed.
    escribir_cache(raiz_cache / "pagespeed", "clave_ps", {"valor": 2})

    # Ejecuta invalidación sobre la raíz.
    total = invalidar_cache(raiz_cache)

    # Verifica que se eliminen ambas entradas.
    assert total == 2
