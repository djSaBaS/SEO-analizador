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
- Perfiles de generación compuesta y degradación elegante de exportadores (`test_cli_generation_profiles.py`).
- Generación y consistencia de narrativa IA (`test_gemini_client.py`).
- Exportadores y jerarquía documental (`test_reporters.py`, `test_html_export.py`), incluyendo validaciones de capa semántica común, bloque meta completo, nuevos tipos de bloque semántico explícito con compatibilidad legacy, presencia de periodo visible en Word/PDF/HTML/Excel, fallback `No disponible` cuando faltan fechas, consolidación de contenido por URL con conteos agregados coherentes frente a `Errores`, fusión determinista de campos escalares para evitar dependencia del orden de entrada, coherencia cruzada de títulos principales entre formatos, no regresión cuando se personaliza el modelo semántico y no consumo directo de markdown IA en layout final DOCX/PDF/HTML.
- Reglas de indexación y rastreo (`test_indexacion.py`).

## Ejecución
```bash
pytest -q
```

- Incluye cobertura de regresión para la separación modular de exportadores en `seo_auditor/reporters/` sin romper el contrato público de la CLI.
