# Importa la función de saneamiento para validar robustez en PDF.
from seo_auditor.reporters import sanear_texto_para_pdf


# Verifica que el saneamiento escape etiquetas potencialmente problemáticas.
def test_sanear_texto_para_pdf_escapa_marcado_html() -> None:
    """Comprueba que el texto con etiquetas HTML se escape para reportlab."""

    # Define un texto con etiquetas que pueden romper el parser de reportlab.
    texto = "Etiqueta <link rel='canonical' href='https://ejemplo.com'> y <b>negrita</b>."

    # Ejecuta el saneamiento antes de generar el PDF.
    saneado = sanear_texto_para_pdf(texto)

    # Verifica que la etiqueta se haya escapado correctamente.
    assert "&lt;link rel='canonical' href='https://ejemplo.com'&gt;" in saneado

    # Verifica que también se haya escapado el cierre de negrita.
    assert "&lt;b&gt;negrita&lt;/b&gt;" in saneado
