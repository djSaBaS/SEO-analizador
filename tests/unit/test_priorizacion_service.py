"""Pruebas unitarias del servicio de priorización."""

from seo_auditor.models import HallazgoSeo
from seo_auditor.services.priorizacion_service import priorizar_hallazgos


def test_priorizar_hallazgos_acepta_tupla_legacy() -> None:
    """Verifica compatibilidad con iterables legacy distintos de list."""
    hallazgos = (
        HallazgoSeo(
            tipo="tecnico",
            severidad="alta",
            descripcion="Error crítico",
            recomendacion="Corregir",
            area="indexacion",
            impacto="alto",
            esfuerzo="medio",
            prioridad="P1",
        ),
        HallazgoSeo(
            tipo="contenido",
            severidad="media",
            descripcion="Meta ausente",
            recomendacion="Completar",
            area="contenido",
            impacto="medio",
            esfuerzo="bajo",
            prioridad="P3",
        ),
    )

    resultado = priorizar_hallazgos(hallazgos)

    assert "score" in resultado
    assert resultado["componentes"]["hallazgos_totales"] == 2

