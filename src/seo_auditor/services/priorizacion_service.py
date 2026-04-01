"""Servicios de priorización y scoring explicable para auditorías."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from seo_auditor.models import AuditoriaResult


def priorizar_hallazgos(auditoria_result: AuditoriaResult | Iterable[object]) -> dict[str, object]:
    """Calcula una priorización explicable a partir de un resultado de auditoría consolidado."""
    if isinstance(auditoria_result, AuditoriaResult):
        resultado = auditoria_result.auditoria
        hallazgos = [hallazgo for url in resultado.resultados for hallazgo in url.hallazgos]
        fuentes_activas = list(resultado.fuentes_activas)
        fuentes_fallidas = list(resultado.fuentes_fallidas)
        urls_analizadas = auditoria_result.resumen_ejecucion.total_urls_analizadas
    else:
        hallazgos = list(auditoria_result)
        fuentes_activas = []
        fuentes_fallidas = []
        urls_analizadas = 0
    total_hallazgos = len(hallazgos)

    conteo_prioridad = Counter(getattr(h, "prioridad", "P4") for h in hallazgos)
    conteo_severidad = Counter(getattr(h, "severidad", "baja") for h in hallazgos)
    conteo_area = Counter(getattr(h, "area", "sin_area") for h in hallazgos)

    pesos = {"P1": 100, "P2": 70, "P3": 40, "P4": 15}
    score_base = sum(pesos.get(prioridad, 10) * cantidad for prioridad, cantidad in conteo_prioridad.items())
    score_normalizado = round(score_base / max(total_hallazgos, 1), 2)

    motivos = []
    if conteo_prioridad.get("P1", 0) > 0:
        motivos.append(f"Se detectaron {conteo_prioridad['P1']} hallazgos críticos (P1).")
    if conteo_severidad.get("alta", 0) > 0:
        motivos.append(f"Hay {conteo_severidad['alta']} incidencias con severidad alta.")
    area_dominante = conteo_area.most_common(1)[0][0] if conteo_area else "sin_area"
    motivos.append(f"El área con más deuda es '{area_dominante}'.")

    componentes = {
        "hallazgos_totales": total_hallazgos,
        "prioridades": dict(conteo_prioridad),
        "severidades": dict(conteo_severidad),
        "areas": dict(conteo_area),
        "fuentes_activas": fuentes_activas,
        "fuentes_fallidas": fuentes_fallidas,
        "urls_analizadas": urls_analizadas,
    }
    return {"score": score_normalizado, "motivos": motivos, "componentes": componentes}
