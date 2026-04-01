from types import SimpleNamespace

from seo_auditor.models import DatosAnalytics, DatosSearchConsole, ResultadoAuditoria
from seo_auditor.services.informe_service import InformeService


def test_informe_service_filtra_secciones_por_fuentes() -> None:
    resultado = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=0,
        resultados=[],
        cliente="Ejemplo",
        fecha_ejecucion="2026-04-01",
        gestor="Gestor",
        search_console=DatosSearchConsole(activo=False),
        analytics=DatosAnalytics(activo=True),
        resumen_ia="",
    )
    servicio = InformeService()
    modelo = servicio.construir_modelo_documental(resultado, configuracion=SimpleNamespace(ga_enabled=False, gemini_api_key=""))
    titulos = [seccion.get("titulo") for seccion in modelo["secciones"]]
    assert titulos[0] == "Portada"
    assert "Visibilidad orgánica real" not in titulos
    assert "Comportamiento y conversión" not in titulos
    assert "Resumen ejecutivo" in titulos
    assert titulos[-1] == "Anexo técnico"


def test_informe_service_preparar_informe_mantiene_markdown_auxiliar() -> None:
    resultado = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=0,
        resultados=[],
        cliente="Ejemplo",
        fecha_ejecucion="2026-04-01",
        gestor="Gestor",
        resumen_ia="Texto IA",
    )
    servicio = InformeService()
    paquete = servicio.preparar_informe(resultado, configuracion=None, incluir_markdown_ia=True)
    assert "modelo_semantico" in paquete
    assert paquete["markdown_ia_auxiliar"] == "Texto IA"
