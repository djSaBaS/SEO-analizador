# Auditor SEO Pro con Python + Gemini

Herramienta de auditoría SEO técnica y ejecutiva para agencia, con exportación profesional a JSON, Excel, Word, PDF y Markdown IA.

## Objetivo
- Analizar sitemaps XML.
- Auditar URLs y señales SEO on-page.
- Clasificar incidencias automáticamente por severidad, área, impacto, esfuerzo y prioridad.
- Generar entregables orientados a cliente final.
- Reducir consumo de tokens en IA mediante contexto agregado.

## Estructura
- `src/`: código fuente del proyecto.
- `tests/`: pruebas automáticas.
- `docs/`: documentación viva.
- `version.md`: historial funcional del proyecto.
- `agent.md`: normas para humanos y agentes IA.

## Requisitos
- Python 3.11 o superior.
- Conexión a internet para auditar webs y para usar Gemini.
- Clave de API de Google AI Studio si quieres usar IA.

## Crear entorno virtual en Windows CMD
```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Crear entorno virtual en Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Crear entorno virtual en Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución básica
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap_index.xml --output ./salidas
```

## Ejecución con IA
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap_index.xml --output ./salidas --usar-ia
```

## Parámetros CLI clave
- `--gestor "Nombre Apellidos"`: define gestor del informe (por defecto `Juan Antonio Sánchez Plaza`).
- `--max-muestras-ia 15`: limita muestras agregadas enviadas a Gemini para reducir tokens.

## Estructura de salida
La salida siempre se organiza por dominio + fecha real de ejecución:

```text
<output>/<slug_dominio>/<YYYY-MM-DD>/
```

Ejemplo:

```text
./salidas/jmmoldes/2026-03-19/
```

## Entregables generados
- `informe_seo_<cliente>_<fecha>_tecnico.json`
- `informe_seo_<cliente>_<fecha>.xlsx`
- `informe_seo_<cliente>_<fecha>.docx`
- `informe_seo_<cliente>_<fecha>.pdf`
- `informe_seo_<cliente>_<fecha>_ia.md` (si se usa IA)

## Excel profesional
- Hoja inicial `Dashboard`.
- Hoja `Errores` con seguimiento editable (`estado`, `resuelto`, `responsable`, `observaciones`).
- Hoja `Roadmap` con plan 30/60/90 días.
- Métricas dinámicas con fórmulas y gráficos.

## Ejecutar tests
```bash
pytest -q
```
