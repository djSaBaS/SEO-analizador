from seo_auditor.documentacion.builders.secciones import construir_jerarquia_visible, construir_secciones_desde_ia
from seo_auditor.models import DatosAnalytics, DatosSearchConsole, ResultadoAuditoria


def test_builders_construir_secciones_desde_ia_limpia_markdown() -> None:
    texto = "## Resumen ejecutivo\n**Texto clave**\n- Punto uno\n---\n### Roadmap\n1. Acción A"
    secciones = construir_secciones_desde_ia(texto)
    assert len(secciones) >= 2
    assert "**" not in " ".join(str(item) for seccion in secciones for item in seccion["items"])


def test_builders_construir_jerarquia_visible_filtra_fuentes() -> None:
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-25",
        gestor="Gestor",
        search_console=DatosSearchConsole(activo=False),
        analytics=DatosAnalytics(activo=False),
    )
    jerarquia = construir_jerarquia_visible(auditoria)
    assert "Comportamiento y conversión" not in jerarquia
    assert "Visibilidad orgánica real" not in jerarquia
