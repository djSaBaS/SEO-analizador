from seo_auditor.documentacion.shared.estilos import calcular_col_widths_pdf, color_pastel_severidad
from seo_auditor.documentacion.shared.helpers import reemplazar_emojis_problematicos, sanear_texto_para_pdf


def test_shared_helpers_sanean_texto_pdf() -> None:
    texto = "Etiqueta <link rel='canonical' href='https://ejemplo.com'>"
    salida = sanear_texto_para_pdf(texto)
    assert "&lt;link rel='canonical' href='https://ejemplo.com'&gt;" in salida


def test_shared_helpers_reemplaza_emojis() -> None:
    salida = reemplazar_emojis_problematicos("✅ OK ⚠️ revisar ❌ fallo")
    assert "Validado" in salida and "Revisión recomendada" in salida and "Incidencia detectada" in salida


def test_shared_estilos_exponen_api() -> None:
    assert color_pastel_severidad("alta") == "#fde8e8"
    anchos = calcular_col_widths_pdf(["URL", "Problema"], [["https://ejemplo.com", "Falta title"]], 400.0)
    assert len(anchos) == 2
    assert abs(sum(anchos) - 400.0) < 0.001
