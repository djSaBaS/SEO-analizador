# Auditor SEO Pro con Python + Gemini

Herramienta de auditoría SEO técnica y ejecutiva para agencia, con exportación profesional a JSON, Excel, Word, PDF y Markdown IA.

## Objetivo
- Analizar sitemaps XML.
- Auditar URLs y señales SEO on-page.
- Clasificar incidencias automáticamente por severidad, área, impacto, esfuerzo y prioridad.
- Generar entregables orientados a cliente final.
- Reducir consumo de tokens en IA mediante contexto agregado.

## Requisitos
- Python 3.11 o superior.
- Conexión a internet para auditar webs y para usar Gemini.
- Clave de API de Google AI Studio si quieres usar IA.

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
```text
<output>/<slug_dominio>/<YYYY-MM-DD>/
```

## Calidad documental (esta iteración)
- Word con portada corporativa, tabla KPI, secciones editoriales reales, tablas ejecutivas y anexo técnico separado.
- PDF con estructura equivalente y contenido saneado para evitar errores por markup no compatible.
- Capa de transformación IA → `sections = [{titulo, tipo, items}]` para eliminar markdown crudo en Word/PDF.

## Excel profesional
- Hoja inicial `Dashboard` con layout de rejilla fija y gráficos sin solaparse.
- Hoja `Errores` con estilo operativo (wrap text, alineación superior, filtros, freeze panes, validación Sí/No).
- Hoja `Roadmap` para seguimiento 30/60/90 días.
- Hoja auxiliar oculta `AuxDashboard` para cálculos y rangos de gráficos.
- Score SEO ponderado y documentado también en JSON/Excel.

## Ejecutar tests
```bash
pytest -q
```
