"""Pruebas del servicio de coherencia de dominios entre auditoría y fuentes externas."""

# Importa utilidades de coherencia para validaciones de dominio.
from seo_auditor.services.coherencia_fuentes_service import (
    construir_detalle_incompatibilidad,
    dominios_coherentes,
    normalizar_host_fuente,
)


# Valida normalización de formatos equivalentes de dominio.
def test_normalizar_host_fuente_acepta_sc_domain_y_www() -> None:
    """Comprueba que la normalización elimine prefijos y devuelva host canónico."""

    # Verifica normalización de propiedad GSC tipo sc-domain.
    assert normalizar_host_fuente("sc-domain:colegiolegamar.com") == "colegiolegamar.com"

    # Verifica normalización de URL con www y barra final.
    assert normalizar_host_fuente("https://www.colegiolegamar.com/") == "colegiolegamar.com"


# Valida comparación positiva para dominios equivalentes.
def test_dominios_coherentes_equivalentes() -> None:
    """Comprueba que dominios equivalentes se marquen como coherentes."""

    # Verifica coherencia entre sitemap y GSC URL-prefix.
    assert (
        dominios_coherentes("https://humanitaseducacion.com/sitemap_index.xml", "https://www.humanitaseducacion.com/")
        is True
    )


# Valida comparación negativa para dominios distintos.
def test_dominios_coherentes_incompatibles() -> None:
    """Comprueba que dominios distintos se marquen como incompatibles."""

    # Verifica incompatibilidad entre dominio auditado y propiedad externa distinta.
    assert dominios_coherentes("https://humanitaseducacion.com/sitemap.xml", "sc-domain:colegiolegamar.com") is False


# Valida construcción de mensaje estándar de incompatibilidad.
def test_construir_detalle_incompatibilidad_contiene_dominios() -> None:
    """Comprueba que el detalle de incompatibilidad sea legible y trazable."""

    # Genera mensaje de incompatibilidad para auditoría de ejemplo.
    detalle = construir_detalle_incompatibilidad(
        "search_console",
        "sc-domain:colegiolegamar.com",
        "https://humanitaseducacion.com/sitemap.xml",
    )

    # Verifica que el mensaje incluya nombre de fuente.
    assert "search_console incompatible" in detalle

    # Verifica que el mensaje incluya dominio auditado normalizado.
    assert "humanitaseducacion.com" in detalle
