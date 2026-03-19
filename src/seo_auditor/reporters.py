# Importa JSON para exportar datos técnicos trazables.
import json

# Importa contador para cálculos agregados.
from collections import Counter

# Importa la clase Path para gestionar rutas de forma robusta.
from pathlib import Path

# Importa objetos para construir estilos de Word.
from docx import Document

# Importa utilidades de estilo de Word.
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Importa tamaño de fuente y color de Word.
from docx.shared import Pt, RGBColor

# Importa utilidades de PDF para generar un informe portable.
from reportlab.lib import colors

# Importa tamaño de página del PDF.
from reportlab.lib.pagesizes import A4

# Importa estilos tipográficos para PDF.
from reportlab.lib.styles import getSampleStyleSheet

# Importa utilidades avanzadas de maquetación PDF.
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Importa utilidades de openpyxl para Excel profesional.
from openpyxl import Workbook

# Importa estilos y colores de openpyxl.
from openpyxl.styles import Alignment, Font, PatternFill

# Importa herramientas de tabla de openpyxl.
from openpyxl.worksheet.table import Table as ExcelTable, TableStyleInfo

# Importa validaciones de datos para celdas editables.
from openpyxl.worksheet.datavalidation import DataValidation

# Importa gráficos de Excel.
from openpyxl.chart import PieChart, BarChart, Reference

# Importa los modelos del dominio del proyecto.
from seo_auditor.models import ResultadoAuditoria


# Define el orden de severidad para visualización homogénea.
ORDEN_SEVERIDAD = ["crítica", "alta", "media", "baja", "informativa"]


# Construye un prefijo de nombre de archivo legible y consistente.
def construir_prefijo_archivo(resultado: ResultadoAuditoria) -> str:
    """
    Genera un prefijo de naming profesional para entregables.
    """

    # Limpia el nombre del cliente para convertirlo en parte de archivo.
    cliente = resultado.cliente.lower().replace(" ", "_")

    # Devuelve el prefijo homogéneo de archivos exportados.
    return f"informe_seo_{cliente}_{resultado.fecha_ejecucion}"


# Convierte el resultado a una estructura tabular cómoda para exportación.
def construir_filas(resultado: ResultadoAuditoria) -> list[dict]:
    """
    Convierte el resultado de auditoría a una lista de filas tabulares.
    """

    # Inicializa la colección de filas tabulares.
    filas: list[dict] = []

    # Recorre cada URL auditada para convertirla a filas de incidencias.
    for item in resultado.resultados:
        # Inserta fila vacía de control cuando no haya hallazgos para mantener trazabilidad.
        if not item.hallazgos:
            # Añade una fila saneada preparada para seguimiento.
            filas.append(
                {
                    "url": item.url,
                    "url_final": item.url_final,
                    "tipo": item.tipo,
                    "estado_http": item.estado_http,
                    "redirecciona": "Sí" if item.redirecciona else "No",
                    "title": item.title,
                    "h1": item.h1,
                    "meta_description": item.meta_description,
                    "canonical": item.canonical or "",
                    "noindex": "Sí" if item.noindex else "No",
                    "problema": "",
                    "recomendacion": "",
                    "severidad": "informativa",
                    "area": "Calidad",
                    "impacto": "Bajo",
                    "esfuerzo": "Bajo",
                    "prioridad": "P4",
                    "estado": "Pendiente",
                    "resuelto": "No",
                    "responsable": "",
                    "observaciones": item.error or "Sin incidencias críticas",
                }
            )

            # Continúa con la siguiente URL auditada.
            continue

        # Recorre hallazgos para generar una fila por incidencia.
        for hallazgo in item.hallazgos:
            # Añade una fila con los campos clave de auditoría y seguimiento.
            filas.append(
                {
                    "url": item.url,
                    "url_final": item.url_final,
                    "tipo": item.tipo,
                    "estado_http": item.estado_http,
                    "redirecciona": "Sí" if item.redirecciona else "No",
                    "title": item.title,
                    "h1": item.h1,
                    "meta_description": item.meta_description,
                    "canonical": item.canonical or "",
                    "noindex": "Sí" if item.noindex else "No",
                    "problema": hallazgo.descripcion,
                    "recomendacion": hallazgo.recomendacion,
                    "severidad": hallazgo.severidad,
                    "area": hallazgo.area,
                    "impacto": hallazgo.impacto,
                    "esfuerzo": hallazgo.esfuerzo,
                    "prioridad": hallazgo.prioridad,
                    "estado": "Pendiente",
                    "resuelto": "No",
                    "responsable": "",
                    "observaciones": item.error or "",
                }
            )

    # Devuelve las filas preparadas para cualquier exportador.
    return filas


# Garantiza que la carpeta de salida exista antes de escribir archivos.
def asegurar_directorio(path_salida: Path) -> None:
    """
    Crea la carpeta de salida si no existe.
    """

    # Crea el directorio y sus padres sin fallar si ya existen.
    path_salida.mkdir(parents=True, exist_ok=True)


# Calcula métricas ejecutivas agregadas para informes.
def calcular_metricas(resultado: ResultadoAuditoria) -> dict[str, int | float | dict[str, int]]:
    """
    Calcula métricas ejecutivas reutilizables por todos los reportes.
    """

    # Inicializa acumuladores básicos.
    total_incidencias = 0
    urls_sanas = 0
    urls_redireccion = 0
    urls_error_http = 0
    urls_sin_title = 0
    urls_sin_h1 = 0
    urls_sin_meta = 0
    urls_sin_canonical = 0
    urls_noindex = 0

    # Inicializa distribución por severidad y tipo.
    severidades: Counter[str] = Counter()
    tipos: Counter[str] = Counter()

    # Recorre resultados para consolidar valores.
    for item in resultado.resultados:
        # Cuenta incidencias globales.
        total_incidencias += len(item.hallazgos)

        # Incrementa URLs sanas cuando no hay hallazgos.
        if not item.hallazgos:
            urls_sanas += 1

        # Incrementa contador de redirecciones.
        if item.redirecciona:
            urls_redireccion += 1

        # Incrementa contador de errores HTTP.
        if item.estado_http >= 400 or item.estado_http == 0:
            urls_error_http += 1

        # Incrementa métricas de campos vacíos.
        if not item.title:
            urls_sin_title += 1
        if not item.h1:
            urls_sin_h1 += 1
        if not item.meta_description:
            urls_sin_meta += 1
        if not item.canonical:
            urls_sin_canonical += 1
        if item.noindex:
            urls_noindex += 1

        # Recorre hallazgos para distribución por severidad y tipo.
        for hallazgo in item.hallazgos:
            severidades[hallazgo.severidad] += 1
            tipos[hallazgo.tipo] += 1

    # Define pesos de scoring por severidad.
    pesos = {"crítica": 25, "alta": 12, "media": 6, "baja": 2, "informativa": 1}

    # Calcula penalización acumulada por incidencias detectadas.
    penalizacion = sum(severidades.get(severidad, 0) * peso for severidad, peso in pesos.items())

    # Calcula score SEO global limitado a 0-100.
    score = max(0, min(100, 100 - penalizacion))

    # Devuelve métrica agregada lista para renderizado.
    return {
        "total_urls": resultado.total_urls,
        "total_incidencias": total_incidencias,
        "severidades": dict(severidades),
        "tipos": dict(tipos),
        "urls_sanas": urls_sanas,
        "urls_redireccion": urls_redireccion,
        "urls_error_http": urls_error_http,
        "urls_sin_title": urls_sin_title,
        "urls_sin_h1": urls_sin_h1,
        "urls_sin_meta": urls_sin_meta,
        "urls_sin_canonical": urls_sin_canonical,
        "urls_noindex": urls_noindex,
        "score": score,
    }


# Exporta el resultado técnico en formato JSON.
def exportar_json(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un JSON técnico con todos los resultados y metadatos.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo JSON técnico.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}_tecnico.json"

    # Construye un diccionario serializable con todos los resultados.
    contenido = {
        "sitemap": resultado.sitemap,
        "cliente": resultado.cliente,
        "gestor": resultado.gestor,
        "fecha_ejecucion": resultado.fecha_ejecucion,
        "total_urls": resultado.total_urls,
        "resumen_ia": resultado.resumen_ia,
        "metricas": calcular_metricas(resultado),
        "resultados": construir_filas(resultado),
    }

    # Escribe el JSON con codificación UTF-8 legible.
    destino.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")

    # Devuelve la ruta final del archivo generado.
    return destino


# Exporta el detalle tabular a Excel.
def exportar_excel(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un Excel profesional con dashboard y seguimiento.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo Excel final.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}.xlsx"

    # Construye el libro de trabajo vacío.
    libro = Workbook()

    # Selecciona la hoja activa para convertirla en Dashboard.
    hoja_dashboard = libro.active

    # Renombra la hoja inicial como Dashboard.
    hoja_dashboard.title = "Dashboard"

    # Crea la hoja de incidencias como base de datos.
    hoja_errores = libro.create_sheet("Errores")

    # Crea la hoja de roadmap para planificación.
    hoja_roadmap = libro.create_sheet("Roadmap")

    # Construye las filas de incidencias.
    filas = construir_filas(resultado)

    # Obtiene los encabezados desde la primera fila o define fallback.
    encabezados = list(filas[0].keys()) if filas else []

    # Escribe encabezados de la tabla de errores.
    for indice_columna, encabezado in enumerate(encabezados, start=1):
        hoja_errores.cell(row=1, column=indice_columna, value=encabezado)

    # Escribe cada fila de incidencia en la hoja de errores.
    for indice_fila, fila in enumerate(filas, start=2):
        for indice_columna, encabezado in enumerate(encabezados, start=1):
            hoja_errores.cell(row=indice_fila, column=indice_columna, value=fila[encabezado])

    # Crea una tabla visual si existen filas de datos.
    if filas:
        rango_tabla = f"A1:U{len(filas) + 1}"
        tabla = ExcelTable(displayName="TablaErrores", ref=rango_tabla)
        estilo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        tabla.tableStyleInfo = estilo
        hoja_errores.add_table(tabla)

    # Aplica formato básico de encabezados.
    for celda in hoja_errores[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(fill_type="solid", fgColor="1F4E78")

    # Congela paneles para facilitar seguimiento.
    hoja_errores.freeze_panes = "A2"

    # Activa filtros automáticos para la tabla completa.
    if filas:
        hoja_errores.auto_filter.ref = f"A1:U{len(filas) + 1}"

    # Ajusta anchos de columnas con criterio profesional.
    anchos = [35, 35, 12, 12, 12, 25, 25, 30, 30, 10, 45, 45, 12, 15, 12, 12, 10, 12, 10, 18, 30]
    for indice_columna, ancho in enumerate(anchos, start=1):
        hoja_errores.column_dimensions[chr(64 + indice_columna)].width = ancho

    # Aplica colores suaves por severidad.
    colores_severidad = {
        "crítica": "F8CBAD",
        "alta": "FCE4D6",
        "media": "FFF2CC",
        "baja": "E2F0D9",
        "informativa": "D9E1F2",
    }
    for fila_excel in range(2, len(filas) + 2):
        severidad = str(hoja_errores.cell(row=fila_excel, column=13).value).lower()
        color = colores_severidad.get(severidad)
        if color:
            for columna in range(1, 22):
                hoja_errores.cell(row=fila_excel, column=columna).fill = PatternFill(fill_type="solid", fgColor=color)

    # Añade validación Sí/No para columna resuelto.
    validacion_resuelto = DataValidation(type="list", formula1='"Sí,No"', allow_blank=False)
    hoja_errores.add_data_validation(validacion_resuelto)
    validacion_resuelto.add(f"S2:S{len(filas) + 1}")

    # Calcula métricas de alto nivel.
    metricas = calcular_metricas(resultado)

    # Escribe cabecera del dashboard.
    hoja_dashboard["A1"] = "Dashboard SEO"
    hoja_dashboard["A1"].font = Font(size=16, bold=True, color="1F4E78")
    hoja_dashboard["A2"] = f"Cliente: {resultado.cliente}"
    hoja_dashboard["A3"] = f"Gestor: {resultado.gestor}"
    hoja_dashboard["A4"] = f"Fecha de ejecución: {resultado.fecha_ejecucion}"

    # Escribe métricas principales en tarjetas textuales.
    hoja_dashboard["A6"] = "Total de URLs"
    hoja_dashboard["B6"] = metricas["total_urls"]
    hoja_dashboard["A7"] = "Total incidencias"
    hoja_dashboard["B7"] = "=COUNTA(Errores!K2:K1048576)-COUNTBLANK(Errores!K2:K1048576)"
    hoja_dashboard["A8"] = "URLs sanas"
    hoja_dashboard["B8"] = metricas["urls_sanas"]
    hoja_dashboard["A9"] = "URLs redirección"
    hoja_dashboard["B9"] = metricas["urls_redireccion"]
    hoja_dashboard["A10"] = "URLs error HTTP"
    hoja_dashboard["B10"] = metricas["urls_error_http"]
    hoja_dashboard["A11"] = "Sin title"
    hoja_dashboard["B11"] = metricas["urls_sin_title"]
    hoja_dashboard["A12"] = "Sin H1"
    hoja_dashboard["B12"] = metricas["urls_sin_h1"]
    hoja_dashboard["A13"] = "Sin meta description"
    hoja_dashboard["B13"] = metricas["urls_sin_meta"]
    hoja_dashboard["A14"] = "Sin canonical"
    hoja_dashboard["B14"] = metricas["urls_sin_canonical"]
    hoja_dashboard["A15"] = "Con noindex"
    hoja_dashboard["B15"] = metricas["urls_noindex"]
    hoja_dashboard["A16"] = "Score SEO global"
    hoja_dashboard["B16"] = metricas["score"]
    hoja_dashboard["A17"] = "% incidencias resueltas"
    hoja_dashboard["B17"] = "=IF(B7=0,0,COUNTIF(Errores!S2:S1048576,\"Sí\")/B7)"

    # Crea bloque auxiliar de severidades para gráficas.
    hoja_dashboard["D6"] = "Severidad"
    hoja_dashboard["E6"] = "Cantidad"
    for indice, severidad in enumerate(ORDEN_SEVERIDAD, start=7):
        hoja_dashboard[f"D{indice}"] = severidad.title()
        hoja_dashboard[f"E{indice}"] = f"=COUNTIF(Errores!M2:M1048576,\"{severidad}\")"

    # Crea bloque auxiliar de tipo de error para gráfica.
    hoja_dashboard["G6"] = "Tipo"
    hoja_dashboard["H6"] = "Cantidad"
    tipos = list(metricas["tipos"].keys()) or ["técnico"]
    for indice, tipo in enumerate(tipos[:6], start=7):
        hoja_dashboard[f"G{indice}"] = tipo.title()
        hoja_dashboard[f"H{indice}"] = f"=COUNTIF(Errores!C2:C1048576,\"{tipo}\")"

    # Crea bloque de estado correctas vs incidencias.
    hoja_dashboard["J6"] = "Estado"
    hoja_dashboard["K6"] = "Cantidad"
    hoja_dashboard["J7"] = "Correctas"
    hoja_dashboard["K7"] = "=B8"
    hoja_dashboard["J8"] = "Con incidencias"
    hoja_dashboard["K8"] = "=B6-B8"

    # Crea gráfico circular de severidades.
    grafico_severidad = PieChart()
    grafico_severidad.title = "Distribución por severidad"
    grafico_severidad.add_data(Reference(hoja_dashboard, min_col=5, min_row=6, max_row=11), titles_from_data=True)
    grafico_severidad.set_categories(Reference(hoja_dashboard, min_col=4, min_row=7, max_row=11))
    hoja_dashboard.add_chart(grafico_severidad, "D13")

    # Crea gráfico de barras por tipo de error.
    grafico_tipos = BarChart()
    grafico_tipos.title = "Distribución por tipo de error"
    grafico_tipos.add_data(Reference(hoja_dashboard, min_col=8, min_row=6, max_row=6 + len(tipos[:6])), titles_from_data=True)
    grafico_tipos.set_categories(Reference(hoja_dashboard, min_col=7, min_row=7, max_row=6 + len(tipos[:6])))
    hoja_dashboard.add_chart(grafico_tipos, "G13")

    # Crea gráfico de progreso de incidencias resueltas.
    grafico_resueltas = PieChart()
    grafico_resueltas.title = "Progreso incidencias resueltas"
    hoja_dashboard["M6"] = "Estado"
    hoja_dashboard["N6"] = "Cantidad"
    hoja_dashboard["M7"] = "Resueltas"
    hoja_dashboard["N7"] = "=COUNTIF(Errores!S2:S1048576,\"Sí\")"
    hoja_dashboard["M8"] = "Pendientes"
    hoja_dashboard["N8"] = "=MAX(B7-N7,0)"
    grafico_resueltas.add_data(Reference(hoja_dashboard, min_col=14, min_row=6, max_row=8), titles_from_data=True)
    grafico_resueltas.set_categories(Reference(hoja_dashboard, min_col=13, min_row=7, max_row=8))
    hoja_dashboard.add_chart(grafico_resueltas, "M13")

    # Crea gráfico de URLs correctas vs incidencias.
    grafico_estado_urls = PieChart()
    grafico_estado_urls.title = "% URLs correctas vs incidencias"
    grafico_estado_urls.add_data(Reference(hoja_dashboard, min_col=11, min_row=6, max_row=8), titles_from_data=True)
    grafico_estado_urls.set_categories(Reference(hoja_dashboard, min_col=10, min_row=7, max_row=8))
    hoja_dashboard.add_chart(grafico_estado_urls, "J13")

    # Da formato de porcentaje a la métrica de resueltos.
    hoja_dashboard["B17"].number_format = "0.00%"

    # Crea encabezados en roadmap.
    hoja_roadmap.append(["Horizonte", "Objetivo", "Acción", "Prioridad", "Responsable", "Estado"])
    hoja_roadmap.append(["30 días", "Corregir bloqueos de indexación", "Resolver 5xx/4xx y redirecciones en sitemap", "P1", resultado.gestor, "Pendiente"])
    hoja_roadmap.append(["60 días", "Optimizar elementos on-page", "Completar title, H1 y meta description faltantes", "P2", resultado.gestor, "Pendiente"])
    hoja_roadmap.append(["90 días", "Consolidar arquitectura", "Revisar canonicals y noindex no deseados", "P2", resultado.gestor, "Pendiente"])

    # Ajusta formato básico del roadmap.
    for celda in hoja_roadmap[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(fill_type="solid", fgColor="1F4E78")
        celda.alignment = Alignment(horizontal="center")

    # Establece la hoja inicial al abrir archivo.
    libro.active = 0

    # Guarda el libro en disco.
    libro.save(destino)

    # Devuelve la ruta del archivo generado.
    return destino


# Exporta un informe ejecutivo en Word.
def exportar_word(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un informe DOCX con estructura profesional de agencia.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta de salida del documento Word.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}.docx"

    # Crea un nuevo documento Word vacío.
    documento = Document()

    # Configura tipografía base del estilo normal.
    estilo_normal = documento.styles["Normal"]
    estilo_normal.font.name = "Calibri"
    estilo_normal.font.size = Pt(11)

    # Añade portada elegante y centrada.
    portada = documento.add_paragraph("INFORME DE AUDITORÍA SEO")
    portada.alignment = WD_ALIGN_PARAGRAPH.CENTER
    portada.runs[0].font.size = Pt(24)
    portada.runs[0].font.bold = True
    portada.runs[0].font.color.rgb = RGBColor(31, 78, 120)

    # Añade metadatos de portada.
    for linea in [f"Cliente: {resultado.cliente}", f"Dominio / sitemap: {resultado.sitemap}", f"Fecha de ejecución: {resultado.fecha_ejecucion}", f"Gestor de la auditoría: {resultado.gestor}"]:
        parrafo = documento.add_paragraph(linea)
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Añade salto para separar portada del contenido.
    documento.add_page_break()

    # Añade bloque de KPIs principales.
    metricas = calcular_metricas(resultado)
    documento.add_heading("Resumen ejecutivo", level=1)
    documento.add_paragraph(f"Total de URLs auditadas: {metricas['total_urls']}")
    documento.add_paragraph(f"Total de incidencias: {metricas['total_incidencias']}")
    documento.add_paragraph(f"Score SEO global (0-100): {metricas['score']}")

    # Inserta texto de IA si existe.
    if resultado.resumen_ia:
        documento.add_heading("Análisis narrativo", level=2)
        documento.add_paragraph(resultado.resumen_ia)

    # Añade bloques solicitados para informe profesional.
    documento.add_heading("Hallazgos críticos", level=1)
    for item in resultado.resultados:
        for hallazgo in item.hallazgos:
            if hallazgo.severidad in {"crítica", "alta"}:
                documento.add_paragraph(f"[{hallazgo.severidad.upper()}] {item.url}: {hallazgo.descripcion}", style="List Bullet")

    documento.add_heading("Quick wins", level=1)
    for item in resultado.resultados:
        for hallazgo in item.hallazgos:
            if hallazgo.esfuerzo == "Bajo" and hallazgo.impacto in {"Muy alto", "Alto", "Medio"}:
                documento.add_paragraph(f"{item.url}: {hallazgo.recomendacion}", style="List Bullet")

    documento.add_heading("Roadmap", level=1)
    documento.add_paragraph("30 días: resolver incidencias críticas de indexación y servidor.")
    documento.add_paragraph("60 días: optimizar metadatos y encabezados prioritarios.")
    documento.add_paragraph("90 días: consolidar canonical, arquitectura y calidad editorial.")

    # Separa anexo técnico claramente.
    documento.add_page_break()
    documento.add_heading("Anexo técnico", level=1)
    for item in resultado.resultados:
        documento.add_heading(item.url, level=2)
        documento.add_paragraph(f"Estado HTTP: {item.estado_http} | Redirección: {'Sí' if item.redirecciona else 'No'} | Noindex: {'Sí' if item.noindex else 'No'}")
        documento.add_paragraph(f"Title: {item.title or 'Sin title'}")
        documento.add_paragraph(f"H1: {item.h1 or 'Sin H1'}")
        documento.add_paragraph(f"Canonical: {item.canonical or 'Sin canonical'}")
        for hallazgo in item.hallazgos:
            documento.add_paragraph(f"[{hallazgo.severidad}] {hallazgo.descripcion} -> {hallazgo.recomendacion}", style="List Bullet")

    # Guarda el documento en la ruta final.
    documento.save(destino)

    # Devuelve la ruta del archivo generado.
    return destino


# Exporta un PDF con estructura similar a Word.
def exportar_pdf(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un PDF profesional alineado con la estructura del DOCX.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta final del PDF.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}.pdf"

    # Crea el documento PDF.
    pdf = SimpleDocTemplate(str(destino), pagesize=A4)

    # Inicializa la lista de elementos de contenido.
    elementos = []

    # Obtiene estilos base de reportlab.
    estilos = getSampleStyleSheet()

    # Añade portada del informe.
    elementos.append(Paragraph("<b>INFORME DE AUDITORÍA SEO</b>", estilos["Title"]))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"Cliente: {resultado.cliente}", estilos["Normal"]))
    elementos.append(Paragraph(f"Dominio / sitemap: {resultado.sitemap}", estilos["Normal"]))
    elementos.append(Paragraph(f"Fecha de ejecución: {resultado.fecha_ejecucion}", estilos["Normal"]))
    elementos.append(Paragraph(f"Gestor: {resultado.gestor}", estilos["Normal"]))
    elementos.append(Spacer(1, 16))

    # Añade bloque de KPIs en tabla visual.
    metricas = calcular_metricas(resultado)
    tabla_kpi = Table([
        ["KPI", "Valor"],
        ["Total URLs", str(metricas["total_urls"])],
        ["Total incidencias", str(metricas["total_incidencias"])],
        ["Score SEO", str(metricas["score"])],
    ])
    tabla_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elementos.append(tabla_kpi)
    elementos.append(Spacer(1, 14))

    # Añade resumen ejecutivo y bloques solicitados.
    elementos.append(Paragraph("<b>Resumen ejecutivo</b>", estilos["Heading2"]))
    elementos.append(Paragraph(resultado.resumen_ia or "No se ha generado resumen con IA en esta ejecución.", estilos["Normal"]))
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph("<b>Hallazgos críticos</b>", estilos["Heading2"]))
    for item in resultado.resultados:
        for hallazgo in item.hallazgos:
            if hallazgo.severidad in {"crítica", "alta"}:
                elementos.append(Paragraph(f"• {item.url}: {hallazgo.descripcion}", estilos["Normal"]))

    # Construye el PDF final.
    pdf.build(elementos)

    # Devuelve la ruta del archivo generado.
    return destino


# Exporta el informe IA en Markdown para edición y revisión humana.
def exportar_markdown_ia(resultado: ResultadoAuditoria, path_salida: Path) -> Path | None:
    """
    Genera un archivo Markdown con el resumen IA y metadatos.
    """

    # Sale sin crear archivo cuando no existe resumen IA.
    if not resultado.resumen_ia:
        return None

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo Markdown.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}_ia.md"

    # Construye encabezado contextual de informe.
    contenido = (
        f"# Informe SEO IA\n\n"
        f"- Cliente: {resultado.cliente}\n"
        f"- Gestor: {resultado.gestor}\n"
        f"- Fecha de ejecución: {resultado.fecha_ejecucion}\n"
        f"- Sitemap: {resultado.sitemap}\n\n"
        f"{resultado.resumen_ia}\n"
    )

    # Escribe el contenido del informe IA en UTF-8.
    destino.write_text(contenido, encoding="utf-8")

    # Devuelve la ruta del archivo generado.
    return destino
