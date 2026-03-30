# src/seo_auditor/reporters/info.md

Paquete modular de exportación documental SEO.

## Responsabilidades por archivo
- `__init__.py`: fachada pública compatible con la CLI y tests históricos (`seo_auditor.reporters`).
- `core.py`: lógica común compartida (modelo semántico, construcción de filas, helpers editoriales y renderizadores base).
- `exportador_word.py`: punto de entrada de exportación DOCX.
- `exportador_pdf.py`: punto de entrada de exportación PDF.
- `exportador_html.py`: punto de entrada de exportación HTML.
- `exportador_excel.py`: punto de entrada de exportación Excel.
- `exportador_json.py`: punto de entrada de exportación JSON técnico.
- `exportador_markdown.py`: punto de entrada de exportación Markdown IA para revisión interna.
- `helpers_documentales.py`: utilidades compartidas de sanitización y limpieza editorial.
- `modelo_documental.py`: acceso explícito al modelo semántico transversal y jerarquía visible.
- `estilos_documentales.py`: constantes y utilidades de estilo compartidas entre formatos.

## Notas operativas
- La separación por exportador permite evolucionar cada formato sin romper el contrato público.
- La lógica funcional común permanece centralizada para evitar duplicación y preservar coherencia entre entregables.
