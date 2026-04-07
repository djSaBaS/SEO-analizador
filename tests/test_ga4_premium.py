# Importa utilidades de fecha para validaciones deterministas.

# Importa módulo GA4 premium bajo prueba.
from seo_auditor import ga4_premium


# Verifica que la comparación anio-anterior gestione correctamente años bisiestos.
def test_resolver_comparacion_anio_anterior_bisiesto() -> None:
    """Comprueba que 2024-02-29 se mapee a 2023-02-28 al restar un año."""

    # Ejecuta resolución de comparación para fecha bisiesta.
    desde, hasta = ga4_premium._resolver_comparacion("2024-02-29", "2024-03-02", "anio-anterior")

    # Verifica ajuste correcto del inicio para año no bisiesto.
    assert desde == "2023-02-28"

    # Verifica ajuste correcto del fin del periodo.
    assert hasta == "2023-03-02"


# Verifica que los insights usen umbrales esperados para detectar casos clave.
def test_construir_insights_detecta_tres_patrones() -> None:
    """Comprueba detección de sin conversión, alto rebote y alto valor."""

    # Construye muestra de landings con escenarios representativos.
    landings = [
        {"landingPagePlusQueryString": "/a", "sessions": 45.0, "conversions": 0.0, "bounceRate": 0.8},
        {"landingPagePlusQueryString": "/b", "sessions": 60.0, "conversions": 3.0, "bounceRate": 0.35},
    ]

    # Ejecuta construcción de insights automáticos.
    insights = ga4_premium._construir_insights(landings)

    # Verifica presencia de insight de tráfico sin conversión.
    assert any("sin conversión" in insight for insight in insights)

    # Verifica presencia de insight de alto rebote.
    assert any("alto rebote" in insight for insight in insights)

    # Verifica presencia de insight de alto valor.
    assert any("alto valor" in insight for insight in insights)
