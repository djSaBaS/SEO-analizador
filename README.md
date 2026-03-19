# Auditor SEO Pro con Python + Gemini

Proyecto base profesional para auditar sitios web desde sitemap, detectar problemas SEO técnicos y generar un informe enriquecido con IA mediante Google AI Studio.

## Objetivo
Este proyecto está pensado para:

- Analizar sitemaps XML.
- Revisar URLs y códigos HTTP.
- Extraer señales SEO on-page básicas.
- Detectar problemas prioritarios.
- Generar un informe técnico en Excel.
- Generar un informe ejecutivo en Word.
- Generar una versión PDF simple a partir del resumen técnico.
- Enriquecer el informe con recomendaciones de IA usando Gemini.

## Estructura
- `src/`: código fuente del proyecto.
- `tests/`: pruebas automáticas.
- `docs/`: documentación viva.
- `scripts/`: scripts de ayuda.
- `version.md`: historial funcional del proyecto.
- `agent.md`: normas para humanos y agentes IA.

## Requisitos
- Python 3.11 o superior.
- Conexión a internet para auditar webs y para usar Gemini.
- Clave de API de Google AI Studio si quieres usar el análisis con IA.

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

## Configuración
1. Copia `.env.example` a `.env`.
2. Añade tu clave en `GEMINI_API_KEY` si quieres activar IA.

## Ejecución básica
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap_index.xml --output ./salidas
```

## Ejecución con IA
```bash
python src/main.py --sitemap https://www.ejemplo.com/sitemap_index.xml --output ./salidas --usar-ia
```

## Qué genera
Dentro de la carpeta de salida se crearán:

- `resultado_tecnico.json`
- `urls_auditadas.xlsx`
- `informe_seo.docx`
- `informe_seo.pdf`
- `informe_ia.md` si se usa Gemini

## Ejecutar tests
```bash
pytest -q
```

## Generar ejecutable .exe
Este proyecto no incluye PyInstaller por defecto para mantener mínimas las dependencias.

Si más adelante quieres convertirlo en ejecutable, puedes hacerlo así:
```bash
pip install pyinstaller
pyinstaller --onefile --name auditor_seo_pro src/main.py
```

## Buenas prácticas incluidas
- Validación de entradas.
- Manejo seguro de errores.
- Separación de responsabilidades.
- Exportación profesional de resultados.
- Tests unitarios y de regresión base.

## Límite intencional de esta base
Esta primera versión está preparada para un uso profesional ligero y seguro. No hace crawling completo del sitio más allá del sitemap. Eso reduce ruido, coste y complejidad. El proyecto queda preparado para crecer por módulos.
