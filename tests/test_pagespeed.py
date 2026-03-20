# Importa utilidades de URL de rendimiento bajo prueba.
from seo_auditor.pagespeed import detectar_home

# Importa transformación IA para validar limpieza editorial.
from seo_auditor.reporters import construir_secciones_desde_ia


# Verifica que la home se detecte desde la raíz del dominio.
def test_detectar_home_prioriza_raiz_dominio() -> None:
    """Comprueba que la detección por defecto devuelva la home del dominio."""

    # Define sitemap de ejemplo.
    sitemap = "https://www.ejemplo.com/page-sitemap.xml"

    # Define URLs sin home explícita.
    urls = ["https://www.ejemplo.com/servicios/", "https://www.ejemplo.com/contacto/"]

    # Ejecuta detección de home.
    home = detectar_home(sitemap, urls)

    # Verifica raíz esperada.
    assert home == "https://www.ejemplo.com/"


# Verifica que la limpieza de markdown quite símbolos crudos.
def test_construir_secciones_desde_ia_elimina_sintaxis_markdown() -> None:
    """Comprueba que la estructura intermedia no arrastre tokens markdown crudos."""

    # Define contenido con marcas markdown prohibidas.
    texto = "### Resumen ejecutivo\n**Mensaje**\n---\n- Punto"

    # Ejecuta transformación de texto IA.
    secciones = construir_secciones_desde_ia(texto)

    # Consolida todo el texto transformado.
    consolidado = " ".join(str(item) for seccion in secciones for item in seccion["items"])

    # Verifica limpieza de símbolos markdown.
    assert "**" not in consolidado and "###" not in consolidado and "---" not in consolidado
