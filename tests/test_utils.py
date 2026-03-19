# Importa pytest para escribir aserciones expresivas.
import pytest

# Importa utilidades del proyecto bajo prueba.
from seo_auditor.utils import es_url_http_valida, inferir_tipo_url, normalizar_url


# Verifica que una URL HTTPS válida sea aceptada.
def test_es_url_http_valida_acepta_url_https() -> None:
    """Comprueba la validación positiva de una URL HTTPS válida."""

    # Ejecuta la validación sobre una URL segura.
    resultado = es_url_http_valida("https://www.ejemplo.com/sitemap.xml")

    # Confirma que la URL se considera válida.
    assert resultado is True, "Se esperaba que una URL HTTPS bien formada fuese válida."


# Verifica que una cadena inválida sea rechazada.
def test_es_url_http_valida_rechaza_texto_invalido() -> None:
    """Comprueba la validación negativa de una entrada no URL."""

    # Ejecuta la validación sobre una cadena no válida.
    resultado = es_url_http_valida("no-es-una-url")

    # Confirma que la entrada se rechaza correctamente.
    assert resultado is False, "Se esperaba que una cadena no URL fuese rechazada."


# Verifica la normalización básica de una URL con barra final.
def test_normalizar_url_elimina_barra_final_no_raiz() -> None:
    """Comprueba que se elimine la barra final en rutas no raíz."""

    # Normaliza una URL de página con barra final.
    resultado = normalizar_url("https://www.ejemplo.com/pagina/")

    # Valida que la barra final haya sido eliminada.
    assert resultado == "https://www.ejemplo.com/pagina", "La URL normalizada no coincide con el valor esperado."


# Verifica la inferencia de tipo categoría.
def test_inferir_tipo_url_detecta_category() -> None:
    """Comprueba que la ruta de categoría se clasifique correctamente."""

    # Clasifica una URL de categoría típica de WordPress.
    resultado = inferir_tipo_url("https://www.ejemplo.com/category/seo/")

    # Valida el tipo lógico esperado.
    assert resultado == "category", "Se esperaba el tipo 'category' para una ruta de categoría."


# Verifica la inferencia de tipo entrada por patrón de fecha.
def test_inferir_tipo_url_detecta_post() -> None:
    """Comprueba que una ruta con fecha se clasifique como entrada."""

    # Clasifica una URL con patrón de fecha.
    resultado = inferir_tipo_url("https://www.ejemplo.com/2026/03/19/post-de-prueba/")

    # Valida el tipo lógico esperado.
    assert resultado == "post", "Se esperaba el tipo 'post' para una ruta con fecha."
