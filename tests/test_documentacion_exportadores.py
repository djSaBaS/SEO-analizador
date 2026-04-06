from pathlib import Path

import pytest

from seo_auditor.documentacion.exportadores.exportador_html import exportar_html
from seo_auditor.documentacion.exportadores.exportador_pdf import exportar_pdf
from seo_auditor.documentacion.exportadores.exportador_word import exportar_word
from seo_auditor.models import HallazgoSeo, ResultadoAuditoria, ResultadoUrl
from seo_auditor.services.informe_service import InformeService


def _auditoria_minima() -> ResultadoAuditoria:
    hallazgo = HallazgoSeo(
        tipo="contenido",
        severidad="alta",
        descripcion="Falta title.",
        recomendacion="Añadir title.",
        area="Contenido",
        impacto="Alto",
        esfuerzo="Bajo",
        prioridad="P1",
    )
    url = ResultadoUrl(
        url="https://ejemplo.com/a",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/a",
        title="",
        h1="H1",
        meta_description="Meta",
        canonical="https://ejemplo.com/a",
        noindex=False,
        hallazgos=[hallazgo],
    )
    return ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[url],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-29",
        gestor="Gestor",
    )


@pytest.mark.parametrize("export_func", [exportar_html, exportar_word, exportar_pdf])
def test_exportadores_consumen_servicio_informe(export_func, monkeypatch, tmp_path: Path) -> None:
    auditoria = _auditoria_minima()
    original = InformeService.preparar_informe
    llamado = {"ok": False}

    def _wrapper(self, resultado, configuracion, incluir_markdown_ia=True):
        llamado["ok"] = True
        return original(self, resultado, configuracion, incluir_markdown_ia)

    monkeypatch.setattr(InformeService, "preparar_informe", _wrapper)
    ruta = export_func(auditoria, tmp_path)
    assert ruta.exists()
    assert llamado["ok"] is True


def test_exportadores_word_pdf_generan_archivos(tmp_path: Path) -> None:
    auditoria = _auditoria_minima()
    ruta_docx = exportar_word(auditoria, tmp_path)
    ruta_pdf = exportar_pdf(auditoria, tmp_path)
    assert ruta_docx.exists() and ruta_docx.suffix == ".docx"
    assert ruta_pdf.exists() and ruta_pdf.suffix == ".pdf"
