"""Servicios de priorización y scoring."""

from collections import Counter


def priorizar_hallazgos(hallazgos):
    """Genera resumen de prioridades a partir del conjunto de hallazgos."""
    contador = Counter(getattr(h, "prioridad", "P4") for h in hallazgos)
    return dict(contador)
