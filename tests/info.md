# tests/info.md

Suite de pruebas unitarias y de regresión.

## Objetivo
Validar estabilidad funcional del CLI, integraciones y exportadores sin romper compatibilidad operativa.

## Cobertura principal
- Utilidades y validación de URLs/fechas (`test_utils.py`).
- Auditoría SEO y clasificación de hallazgos (`test_analyzer.py`).
- Integración y tolerancia de PageSpeed (`test_pagespeed.py`, `test_cli_pagespeed_flow.py`).
- Caché local e invalidación (`test_cache.py`).
- Integraciones opcionales de GSC y GA4 (`test_gsc.py`, `test_ga4.py`).
- Modo dedicado GA4 premium y conectividad CLI (`test_ga4_premium.py`, `test_cli_ga4_premium_mode.py`, `test_cli_connectivity_modes.py`).
- Generación y consistencia de narrativa IA (`test_gemini_client.py`).
- Exportadores y jerarquía documental (`test_reporters.py`, `test_html_export.py`), incluyendo validaciones de capa semántica común, compatibilidad de emojis y explicabilidad de priorización.
- Reglas de indexación y rastreo (`test_indexacion.py`).

## Ejecución
```bash
pytest -q
```
