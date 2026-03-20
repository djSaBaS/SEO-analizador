# Importa JSON para exportar datos técnicos trazables.
import json

# Importa expresiones regulares para parsear texto narrativo con formato mixto.
import re

# Importa contador para cálculos agregados.
from collections import Counter

# Importa la clase Path para gestionar rutas de forma robusta.
from pathlib import Path

# Importa escape para sanear texto potencialmente interpretado como etiquetas XML.
from xml.sax.saxutils import escape

# Importa utilidades para crear hipervínculos nativos en Word.
from docx.oxml import OxmlElement

# Importa utilidades para resolver atributos de XML en Word.
from docx.oxml.ns import qn

# Importa objetos para construir estilos de Word.
from docx import Document

# Importa utilidades de estilo de Word.
from docx.enum.section import WD_SECTION_START

# Importa utilidades de estilo de Word.
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Importa tamaño de fuente y color de Word.
from docx.shared import Pt, RGBColor

# Importa utilidades de PDF para generar un informe portable.
from reportlab.lib import colors

# Importa tamaño de página del PDF.
from reportlab.lib.pagesizes import A4

# Importa estilos tipográficos para PDF.
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

# Importa utilidades avanzadas de maquetación PDF.
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Importa utilidades de openpyxl para Excel profesional.
from openpyxl import Workbook

# Importa gráficos de Excel.
from openpyxl.chart import BarChart, DoughnutChart, PieChart, Reference

# Importa estilos y colores de openpyxl.
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

# Importa validaciones de datos para celdas editables.
from openpyxl.worksheet.datavalidation import DataValidation

# Importa herramientas de tabla de openpyxl.
from openpyxl.worksheet.table import Table as ExcelTable, TableStyleInfo

# Importa los modelos del dominio del proyecto.
from seo_auditor.models import ResultadoAuditoria


# Define el orden de severidad para visualización homogénea.
ORDEN_SEVERIDAD = ["crítica", "alta", "media", "baja", "informativa"]

# Define los títulos objetivo del bloque ejecutivo para render consistente.
SECCIONES_OBJETIVO = [
    "Resumen ejecutivo",
    "Hallazgos críticos",
    "Quick wins",
    "Acciones técnicas",
    "Acciones de contenido",
    "Roadmap",
]


# Construye un prefijo de nombre de archivo legible y consistente.
def construir_prefijo_archivo(resultado: ResultadoAuditoria) -> str:
    """
    Genera un prefijo de naming profesional para entregables.
    """

    # Limpia el nombre del cliente para convertirlo en parte de archivo.
    cliente = resultado.cliente.lower().replace(" ", "_")

    # Devuelve el prefijo homogéneo de archivos exportados.
    return f"informe_seo_{cliente}_{resultado.fecha_ejecucion}"


# Sanea un texto libre para que reportlab no lo interprete como marcado inválido.
def sanear_texto_para_pdf(texto: str) -> str:
    """
    Limpia y escapa texto dinámico para render seguro en Paragraph de reportlab.
    """

    # Normaliza saltos de línea de Windows a formato estándar.
    texto_normalizado = texto.replace("\r\n", "\n").replace("\r", "\n")

    # Escapa caracteres especiales para evitar errores del parser XML interno.
    texto_escapado = escape(texto_normalizado)

    # Devuelve texto saneado para inserción segura en PDF.
    return texto_escapado


# Limpia marcas markdown para evitar texto crudo en DOCX/PDF.
def limpiar_markdown_crudo(texto: str) -> str:
    """
    Elimina marcas markdown frecuentes y deja texto natural legible.
    """

    # Elimina separadores de regla horizontal.
    texto_limpio = re.sub(r"^\s*---+\s*$", "", texto, flags=re.MULTILINE)

    # Elimina encabezados markdown conservando el título.
    texto_limpio = re.sub(r"^\s*#{1,6}\s*", "", texto_limpio, flags=re.MULTILINE)

    # Elimina formato de negrita y cursiva.
    texto_limpio = texto_limpio.replace("**", "").replace("__", "")

    # Elimina backticks de código en línea.
    texto_limpio = texto_limpio.replace("`", "")

    # Devuelve texto normalizado sin espacios extremos por línea.
    return "\n".join(linea.strip() for linea in texto_limpio.splitlines())


# Convierte narrativa IA en secciones internas estructuradas.
def construir_secciones_desde_ia(texto_ia: str | None) -> list[dict[str, object]]:
    """
    Transforma texto narrativo en estructura intermedia `sections` para render estable.
    """

    # Devuelve colección vacía cuando no exista texto IA.
    if not texto_ia:
        return []

    # Limpia markdown crudo y normaliza el contenido.
    texto_limpio = limpiar_markdown_crudo(texto_ia)

    # Inicializa lista de secciones resultado.
    secciones: list[dict[str, object]] = []

    # Inicializa la sección activa por defecto.
    seccion_actual: dict[str, object] = {"titulo": "Resumen ejecutivo", "tipo": "parrafos", "items": []}

    # Recorre línea a línea el texto limpio.
    for linea in texto_limpio.splitlines():
        # Omite líneas completamente vacías.
        if not linea.strip():
            continue

        # Detecta posibles títulos por patrón semántico.
        es_titulo = bool(re.match(r"^(\d+[\)\.]\s+)?(resumen|hallazgos|quick wins|acciones técnicas|acciones de contenido|roadmap|anexo)", linea.lower()))

        # Crea nueva sección cuando se detecta título.
        if es_titulo:
            # Añade sección actual si ya contiene items.
            if seccion_actual["items"]:
                secciones.append(seccion_actual)

            # Extrae el título limpio eliminando numeración inicial.
            titulo = re.sub(r"^\d+[\)\.]\s*", "", linea).strip().title()

            # Inicializa nueva sección vacía.
            seccion_actual = {"titulo": titulo, "tipo": "parrafos", "items": []}

            # Continúa con la siguiente línea del texto.
            continue

        # Detecta viñetas y ajusta tipo de sección.
        if linea.startswith(("- ", "* ", "• ")):
            seccion_actual["tipo"] = "vinetas"
            seccion_actual["items"].append(linea[2:].strip())
            continue

        # Detecta listas numeradas y ajusta tipo de sección.
        if re.match(r"^\d+[\)\.]\s+", linea):
            seccion_actual["tipo"] = "numerada"
            seccion_actual["items"].append(re.sub(r"^\d+[\)\.]\s*", "", linea).strip())
            continue

        # Añade el contenido como párrafo normal.
        seccion_actual["items"].append(linea.strip())

    # Añade la última sección pendiente cuando tenga contenido.
    if seccion_actual["items"]:
        secciones.append(seccion_actual)

    # Devuelve secciones estructuradas y listas para render.
    return secciones


# Convierte el resultado a una estructura tabular cómoda para exportación.
def construir_filas(resultado: ResultadoAuditoria) -> list[dict]:
    """
    Convierte el resultado de auditoría a una lista de filas tabulares.
    """

    # Inicializa la colección de filas tabulares.
    filas: list[dict] = []

    # Recorre cada URL auditada para convertirla a filas de incidencias.
    for item in resultado.resultados:
        # Inserta fila de control cuando no haya hallazgos para mantener trazabilidad.
        if not item.hallazgos:
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
            continue

        # Recorre hallazgos para generar una fila por incidencia.
        for hallazgo in item.hallazgos:
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
def calcular_metricas(resultado: ResultadoAuditoria) -> dict[str, int | float | dict[str, int] | str]:
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

    # Inicializa distribución por severidad, tipo y área.
    severidades: Counter[str] = Counter()
    tipos: Counter[str] = Counter()
    areas: Counter[str] = Counter()

    # Recorre resultados para consolidar valores.
    for item in resultado.resultados:
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

        # Recorre hallazgos para distribuciones agregadas.
        for hallazgo in item.hallazgos:
            severidades[hallazgo.severidad] += 1
            tipos[hallazgo.tipo] += 1
            areas[hallazgo.area] += 1

    # Define pesos de scoring equilibrado por severidad.
    pesos = {"crítica": 10.0, "alta": 6.0, "media": 3.0, "baja": 1.0, "informativa": 0.5}

    # Calcula penalización acumulada ponderada.
    penalizacion = sum(severidades.get(severidad, 0) * peso for severidad, peso in pesos.items())

    # Calcula capacidad máxima teórica de penalización por volumen de URLs.
    max_penalizacion = max(10.0, float(resultado.total_urls) * 10.0)

    # Calcula score SEO global acotado y razonable.
    score = round(max(5.0, min(100.0, 100.0 - (penalizacion / max_penalizacion) * 100.0)), 1)

    # Devuelve métrica agregada lista para renderizado.
    return {
        "total_urls": resultado.total_urls,
        "total_incidencias": total_incidencias,
        "severidades": dict(severidades),
        "tipos": dict(tipos),
        "areas": dict(areas),
        "urls_sanas": urls_sanas,
        "urls_redireccion": urls_redireccion,
        "urls_error_http": urls_error_http,
        "urls_sin_title": urls_sin_title,
        "urls_sin_h1": urls_sin_h1,
        "urls_sin_meta": urls_sin_meta,
        "urls_sin_canonical": urls_sin_canonical,
        "urls_noindex": urls_noindex,
        "score": score,
        "formula_score": "Score = 100 - (penalización_ponderada / (total_urls*10))*100, acotado entre 5 y 100",
    }


# Añade un enlace clicable nativo dentro de un párrafo de Word.
def agregar_hipervinculo(parrafo, url: str, texto_visible: str) -> None:
    """
    Inserta hipervínculo clicable en python-docx usando XML interno.
    """

    # Crea relación externa del documento hacia la URL objetivo.
    relacion_id = parrafo.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)

    # Crea nodo XML de hipervínculo.
    hipervinculo = OxmlElement("w:hyperlink")

    # Asigna relación externa al nodo de hipervínculo.
    hipervinculo.set(qn("r:id"), relacion_id)

    # Crea nodo de run para texto visible.
    run = OxmlElement("w:r")

    # Crea propiedades del run para estilo de enlace.
    propiedades_run = OxmlElement("w:rPr")

    # Crea estilo de run con aspecto de hipervínculo.
    estilo_run = OxmlElement("w:rStyle")

    # Asigna valor de estilo de hipervínculo del tema Word.
    estilo_run.set(qn("w:val"), "Hyperlink")

    # Inserta estilo dentro de propiedades del run.
    propiedades_run.append(estilo_run)

    # Inserta propiedades dentro del run.
    run.append(propiedades_run)

    # Crea nodo de texto para el enlace.
    texto_nodo = OxmlElement("w:t")

    # Asigna texto visible al nodo.
    texto_nodo.text = texto_visible

    # Añade texto al run.
    run.append(texto_nodo)

    # Añade run al hipervínculo.
    hipervinculo.append(run)

    # Inserta hipervínculo dentro del párrafo.
    parrafo._p.append(hipervinculo)


# Aplica formato de legibilidad a una hoja de datos tabulares.
def formatear_hoja_errores(hoja_errores, total_filas: int, total_columnas: int) -> None:
    """
    Mejora legibilidad visual de la hoja de errores para uso operativo real.
    """

    # Define anchos específicos por columna para evitar cortes de contenido.
    anchos = {
        "A": 42,
        "B": 42,
        "C": 14,
        "D": 12,
        "E": 12,
        "F": 24,
        "G": 24,
        "H": 30,
        "I": 30,
        "J": 10,
        "K": 48,
        "L": 48,
        "M": 12,
        "N": 16,
        "O": 12,
        "P": 12,
        "Q": 12,
        "R": 14,
        "S": 10,
        "T": 18,
        "U": 30,
    }

    # Aplica anchos definidos.
    for columna, ancho in anchos.items():
        hoja_errores.column_dimensions[columna].width = ancho

    # Define color por severidad con paleta suave profesional.
    colores_severidad = {
        "crítica": "FDECEA",
        "alta": "FCE8E6",
        "media": "FFF4E5",
        "baja": "EAF4EC",
        "informativa": "E8F0FE",
    }

    # Recorre filas de datos para aplicar estilo de lectura.
    for fila_excel in range(2, total_filas + 1):
        # Lee severidad de la fila actual.
        severidad = str(hoja_errores.cell(row=fila_excel, column=13).value or "").lower()

        # Obtiene color asociado a severidad.
        color = colores_severidad.get(severidad, "FFFFFF")

        # Aplica estilo base a todas las celdas de la fila.
        for columna in range(1, total_columnas + 1):
            celda = hoja_errores.cell(row=fila_excel, column=columna)
            celda.fill = PatternFill(fill_type="solid", fgColor=color)
            celda.alignment = Alignment(vertical="top", wrap_text=True)

    # Ajusta altura de filas para texto largo.
    for fila_excel in range(2, total_filas + 1):
        hoja_errores.row_dimensions[fila_excel].height = 36


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
    Genera un Excel profesional con dashboard legible, hoja auxiliar y gráficos sin solapes.
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

    # Crea la hoja auxiliar de cálculos para dashboard.
    hoja_aux = libro.create_sheet("AuxDashboard")

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

    # Crea tabla visual si existen filas de datos.
    if filas:
        rango_tabla = f"A1:U{len(filas) + 1}"
        tabla = ExcelTable(displayName="TablaErrores", ref=rango_tabla)
        estilo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        tabla.tableStyleInfo = estilo
        hoja_errores.add_table(tabla)

    # Estiliza encabezado de hoja de errores.
    for celda in hoja_errores[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(fill_type="solid", fgColor="1F4E78")
        celda.alignment = Alignment(horizontal="center", vertical="center")

    # Aplica formato operativo de legibilidad.
    formatear_hoja_errores(hoja_errores, len(filas) + 1, len(encabezados) if encabezados else 21)

    # Congela paneles para facilitar seguimiento.
    hoja_errores.freeze_panes = "A2"

    # Activa filtros automáticos para tabla completa.
    if filas:
        hoja_errores.auto_filter.ref = f"A1:U{len(filas) + 1}"

    # Añade validación Sí/No para columna resuelto.
    validacion_resuelto = DataValidation(type="list", formula1='"Sí,No"', allow_blank=False)
    hoja_errores.add_data_validation(validacion_resuelto)
    validacion_resuelto.add(f"S2:S{len(filas) + 1}")

    # Calcula métricas de alto nivel.
    metricas = calcular_metricas(resultado)

    # Prepara hoja auxiliar con tablas para fórmulas y gráficas.
    hoja_aux["A1"] = "Severidad"
    hoja_aux["B1"] = "Cantidad"
    for indice, severidad in enumerate(ORDEN_SEVERIDAD, start=2):
        hoja_aux[f"A{indice}"] = severidad.title()
        hoja_aux[f"B{indice}"] = f"=COUNTIF(Errores!M2:M1048576,\"{severidad}\")"

    # Escribe bloque de áreas en hoja auxiliar.
    hoja_aux["D1"] = "Área"
    hoja_aux["E1"] = "Cantidad"
    areas = sorted(metricas["areas"].keys()) or ["Contenido"]
    for indice, area in enumerate(areas[:6], start=2):
        hoja_aux[f"D{indice}"] = area
        hoja_aux[f"E{indice}"] = f"=COUNTIF(Errores!N2:N1048576,\"{area}\")"

    # Escribe bloque de tipos de problema en hoja auxiliar.
    hoja_aux["G1"] = "Tipo"
    hoja_aux["H1"] = "Cantidad"
    tipos = sorted(metricas["tipos"].keys()) or ["técnico"]
    for indice, tipo in enumerate(tipos[:6], start=2):
        hoja_aux[f"G{indice}"] = tipo
        hoja_aux[f"H{indice}"] = f"=COUNTIF(Errores!C2:C1048576,\"{tipo}\")"

    # Escribe bloque de estado de incidencias.
    hoja_aux["J1"] = "Estado"
    hoja_aux["K1"] = "Cantidad"
    hoja_aux["J2"] = "Resueltas"
    hoja_aux["K2"] = "=COUNTIF(Errores!S2:S1048576,\"Sí\")"
    hoja_aux["J3"] = "Pendientes"
    hoja_aux["K3"] = "=MAX(COUNTIF(Errores!K2:K1048576,\"<>\")-K2,0)"

    # Escribe bloque de estado de URLs.
    hoja_aux["M1"] = "Estado URL"
    hoja_aux["N1"] = "Cantidad"
    hoja_aux["M2"] = "Sanas"
    hoja_aux["N2"] = metricas["urls_sanas"]
    hoja_aux["M3"] = "Con incidencias"
    hoja_aux["N3"] = f"=MAX({resultado.total_urls}-N2,0)"

    # Oculta hoja auxiliar para uso interno de cálculos.
    hoja_aux.sheet_state = "hidden"

    # Define estilo de borde para tarjetas KPI.
    borde = Border(left=Side(style="thin", color="D9D9D9"), right=Side(style="thin", color="D9D9D9"), top=Side(style="thin", color="D9D9D9"), bottom=Side(style="thin", color="D9D9D9"))

    # Escribe cabecera del dashboard.
    hoja_dashboard["A1"] = "Dashboard SEO"
    hoja_dashboard["A1"].font = Font(size=18, bold=True, color="1F4E78")
    hoja_dashboard["A2"] = f"Cliente: {resultado.cliente}"
    hoja_dashboard["A3"] = f"Gestor: {resultado.gestor}"
    hoja_dashboard["A4"] = f"Fecha de ejecución: {resultado.fecha_ejecucion}"

    # Define tarjetas KPI en rejilla superior.
    tarjetas = [
        ("A6", "Total URLs auditadas", resultado.total_urls),
        ("D6", "Total incidencias", "=COUNTIF(Errores!K2:K1048576,\"<>\")"),
        ("G6", "URLs sanas", metricas["urls_sanas"]),
        ("J6", "URLs con redirección", metricas["urls_redireccion"]),
        ("M6", "Score SEO", metricas["score"]),
    ]

    # Recorre tarjetas para pintarlas con estilo uniforme.
    for celda_inicio, etiqueta, valor in tarjetas:
        # Extrae coordenadas base de la tarjeta.
        columna = celda_inicio[0]
        fila = int(celda_inicio[1:])

        # Escribe etiqueta de tarjeta.
        hoja_dashboard[f"{columna}{fila}"] = etiqueta

        # Aplica estilo de etiqueta de tarjeta.
        hoja_dashboard[f"{columna}{fila}"].font = Font(bold=True, color="1F4E78")
        hoja_dashboard[f"{columna}{fila}"].fill = PatternFill(fill_type="solid", fgColor="EAF0F6")
        hoja_dashboard[f"{columna}{fila}"].border = borde

        # Escribe valor de tarjeta en fila siguiente.
        hoja_dashboard[f"{columna}{fila+1}"] = valor

        # Aplica estilo de valor de tarjeta.
        hoja_dashboard[f"{columna}{fila+1}"].font = Font(size=14, bold=True, color="1B1B1B")
        hoja_dashboard[f"{columna}{fila+1}"].fill = PatternFill(fill_type="solid", fgColor="FFFFFF")
        hoja_dashboard[f"{columna}{fila+1}"].border = borde

    # Escribe porcentaje de incidencias resueltas.
    hoja_dashboard["P6"] = "% incidencias resueltas"
    hoja_dashboard["P6"].font = Font(bold=True, color="1F4E78")
    hoja_dashboard["P6"].fill = PatternFill(fill_type="solid", fgColor="EAF0F6")
    hoja_dashboard["P6"].border = borde
    hoja_dashboard["P7"] = "=IF(D7=0,0,AuxDashboard!K2/D7)"
    hoja_dashboard["P7"].number_format = "0.00%"
    hoja_dashboard["P7"].font = Font(size=14, bold=True)
    hoja_dashboard["P7"].border = borde

    # Ajusta ancho de columnas del dashboard para lectura limpia.
    for columna, ancho in {"A": 20, "B": 3, "C": 3, "D": 20, "E": 3, "F": 3, "G": 20, "H": 3, "I": 3, "J": 22, "K": 3, "L": 3, "M": 16, "N": 3, "O": 3, "P": 20}.items():
        hoja_dashboard.column_dimensions[columna].width = ancho

    # Crea gráfico de severidad en bloque izquierdo superior.
    grafico_severidad = DoughnutChart()
    grafico_severidad.title = "Incidencias por severidad"
    grafico_severidad.width = 7.5
    grafico_severidad.height = 6.0
    grafico_severidad.add_data(Reference(hoja_aux, min_col=2, min_row=1, max_row=1 + len(ORDEN_SEVERIDAD)), titles_from_data=True)
    grafico_severidad.set_categories(Reference(hoja_aux, min_col=1, min_row=2, max_row=1 + len(ORDEN_SEVERIDAD)))
    hoja_dashboard.add_chart(grafico_severidad, "B10")

    # Crea gráfico de áreas en bloque derecho superior.
    grafico_areas = BarChart()
    grafico_areas.title = "Incidencias por área"
    grafico_areas.width = 7.5
    grafico_areas.height = 6.0
    grafico_areas.add_data(Reference(hoja_aux, min_col=5, min_row=1, max_row=1 + len(areas[:6])), titles_from_data=True)
    grafico_areas.set_categories(Reference(hoja_aux, min_col=4, min_row=2, max_row=1 + len(areas[:6])))
    hoja_dashboard.add_chart(grafico_areas, "J10")

    # Crea gráfico de tipos de problema en bloque izquierdo inferior.
    grafico_tipos = BarChart()
    grafico_tipos.title = "Tipos de problemas"
    grafico_tipos.width = 7.5
    grafico_tipos.height = 6.0
    grafico_tipos.add_data(Reference(hoja_aux, min_col=8, min_row=1, max_row=1 + len(tipos[:6])), titles_from_data=True)
    grafico_tipos.set_categories(Reference(hoja_aux, min_col=7, min_row=2, max_row=1 + len(tipos[:6])))
    hoja_dashboard.add_chart(grafico_tipos, "B27")

    # Crea gráfico de URLs sanas vs incidencias en bloque derecho inferior.
    grafico_urls = PieChart()
    grafico_urls.title = "URLs sanas vs URLs con incidencias"
    grafico_urls.width = 7.5
    grafico_urls.height = 6.0
    grafico_urls.add_data(Reference(hoja_aux, min_col=14, min_row=1, max_row=3), titles_from_data=True)
    grafico_urls.set_categories(Reference(hoja_aux, min_col=13, min_row=2, max_row=3))
    hoja_dashboard.add_chart(grafico_urls, "J27")

    # Crea gráfico de progreso de resueltas vs pendientes en bloque final.
    grafico_resueltas = PieChart()
    grafico_resueltas.title = "Progreso incidencias resueltas"
    grafico_resueltas.width = 7.5
    grafico_resueltas.height = 5.5
    grafico_resueltas.add_data(Reference(hoja_aux, min_col=11, min_row=1, max_row=3), titles_from_data=True)
    grafico_resueltas.set_categories(Reference(hoja_aux, min_col=10, min_row=2, max_row=3))
    hoja_dashboard.add_chart(grafico_resueltas, "B44")

    # Escribe bloque explicativo de fórmula de score.
    hoja_dashboard["J44"] = "Fórmula score SEO"
    hoja_dashboard["J44"].font = Font(bold=True, color="1F4E78")
    hoja_dashboard["J45"] = metricas["formula_score"]
    hoja_dashboard["J45"].alignment = Alignment(wrap_text=True, vertical="top")

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

    # Ajusta columnas de roadmap para lectura clara.
    for columna, ancho in {"A": 14, "B": 36, "C": 58, "D": 12, "E": 28, "F": 14}.items():
        hoja_roadmap.column_dimensions[columna].width = ancho

    # Establece la hoja inicial al abrir archivo.
    libro.active = 0

    # Guarda el libro en disco.
    libro.save(destino)

    # Devuelve la ruta del archivo generado.
    return destino


# Exporta un informe ejecutivo en Word.
def exportar_word(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un informe DOCX corporativo con estructura editorial y tablas ejecutivas.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta de salida del documento Word.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}.docx"

    # Crea un nuevo documento Word vacío.
    documento = Document()

    # Configura estilo normal como base tipográfica.
    estilo_normal = documento.styles["Normal"]
    estilo_normal.font.name = "Calibri"
    estilo_normal.font.size = Pt(11)

    # Configura encabezado y pie de página de la primera sección.
    seccion = documento.sections[0]
    seccion.header.paragraphs[0].text = f"Informe SEO | {resultado.cliente}"
    seccion.footer.paragraphs[0].text = "Página "

    # Centra verticalmente la portada.
    seccion.start_type = WD_SECTION_START.NEW_PAGE

    # Añade separadores de aire visual para centrar contenido de portada.
    for _ in range(6):
        documento.add_paragraph("")

    # Añade título principal de portada.
    portada_titulo = documento.add_paragraph("INFORME DE AUDITORÍA SEO")
    portada_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    portada_titulo.runs[0].font.size = Pt(28)
    portada_titulo.runs[0].font.bold = True
    portada_titulo.runs[0].font.color.rgb = RGBColor(31, 78, 120)

    # Añade subtítulo corporativo de portada.
    portada_subtitulo = documento.add_paragraph("Auditoría técnica, de indexación y contenidos")
    portada_subtitulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    portada_subtitulo.runs[0].font.size = Pt(14)
    portada_subtitulo.runs[0].font.color.rgb = RGBColor(84, 96, 105)

    # Añade metadatos principales de portada.
    for linea in [f"Cliente: {resultado.cliente}", f"Dominio / sitemap: {resultado.sitemap}", f"Fecha de ejecución: {resultado.fecha_ejecucion}", f"Gestor: {resultado.gestor}"]:
        parrafo = documento.add_paragraph(linea)
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Inserta salto de página tras portada.
    documento.add_page_break()

    # Calcula métricas ejecutivas para tabla KPI.
    metricas = calcular_metricas(resultado)

    # Añade encabezado de resumen ejecutivo.
    documento.add_heading("Resumen ejecutivo", level=1)

    # Crea tabla visual de KPIs clave.
    tabla_kpi = documento.add_table(rows=4, cols=4)
    tabla_kpi.style = "Table Grid"
    tabla_kpi.cell(0, 0).text = "Total URLs"
    tabla_kpi.cell(0, 1).text = str(metricas["total_urls"])
    tabla_kpi.cell(0, 2).text = "Total incidencias"
    tabla_kpi.cell(0, 3).text = str(metricas["total_incidencias"])
    tabla_kpi.cell(1, 0).text = "URLs sanas"
    tabla_kpi.cell(1, 1).text = str(metricas["urls_sanas"])
    tabla_kpi.cell(1, 2).text = "URLs con redirección"
    tabla_kpi.cell(1, 3).text = str(metricas["urls_redireccion"])
    tabla_kpi.cell(2, 0).text = "Score SEO"
    tabla_kpi.cell(2, 1).text = str(metricas["score"])
    tabla_kpi.cell(2, 2).text = "Incidencias altas"
    tabla_kpi.cell(2, 3).text = str(metricas["severidades"].get("alta", 0))
    tabla_kpi.cell(3, 0).text = "Incidencias medias"
    tabla_kpi.cell(3, 1).text = str(metricas["severidades"].get("media", 0))
    tabla_kpi.cell(3, 2).text = "Incidencias bajas"
    tabla_kpi.cell(3, 3).text = str(metricas["severidades"].get("baja", 0))

    # Convierte narrativa IA en estructura editorial intermedia.
    secciones_ia = construir_secciones_desde_ia(resultado.resumen_ia)

    # Crea índice rápido de secciones ya presentes en IA.
    titulos_ia = {str(seccion["titulo"]).lower() for seccion in secciones_ia}

    # Renderiza secciones IA ya estructuradas.
    for seccion_ia in secciones_ia:
        documento.add_heading(str(seccion_ia["titulo"]), level=2)
        if seccion_ia["tipo"] == "vinetas":
            for item in seccion_ia["items"]:
                documento.add_paragraph(str(item), style="List Bullet")
        elif seccion_ia["tipo"] == "numerada":
            for item in seccion_ia["items"]:
                documento.add_paragraph(str(item), style="List Number")
        else:
            for item in seccion_ia["items"]:
                documento.add_paragraph(str(item))

    # Garantiza estructura editorial mínima aunque IA no la haya devuelto completa.
    for titulo in SECCIONES_OBJETIVO:
        if titulo.lower() not in titulos_ia:
            documento.add_heading(titulo, level=2)
            documento.add_paragraph("Sección completada desde datos técnicos de la auditoría.")

    # Añade tabla de hallazgos críticos.
    documento.add_heading("Hallazgos críticos", level=2)
    tabla_criticos = documento.add_table(rows=1, cols=4)
    tabla_criticos.style = "Table Grid"
    tabla_criticos.rows[0].cells[0].text = "Severidad"
    tabla_criticos.rows[0].cells[1].text = "URL"
    tabla_criticos.rows[0].cells[2].text = "Problema"
    tabla_criticos.rows[0].cells[3].text = "Recomendación"
    for fila in construir_filas(resultado):
        if fila["severidad"] in {"crítica", "alta"} and fila["problema"]:
            celdas = tabla_criticos.add_row().cells
            celdas[0].text = str(fila["severidad"]).upper()
            celdas[1].text = str(fila["url"])
            celdas[2].text = str(fila["problema"])
            celdas[3].text = str(fila["recomendacion"])

    # Añade tabla compacta de quick wins.
    documento.add_heading("Quick wins", level=2)
    tabla_quick = documento.add_table(rows=1, cols=3)
    tabla_quick.style = "Table Grid"
    tabla_quick.rows[0].cells[0].text = "URL"
    tabla_quick.rows[0].cells[1].text = "Acción rápida"
    tabla_quick.rows[0].cells[2].text = "Impacto"
    for fila in construir_filas(resultado):
        if fila["esfuerzo"] == "Bajo" and fila["impacto"] in {"Muy alto", "Alto", "Medio"} and fila["problema"]:
            celdas = tabla_quick.add_row().cells
            celdas[0].text = str(fila["url"])
            celdas[1].text = str(fila["recomendacion"])
            celdas[2].text = str(fila["impacto"])

    # Añade tabla roadmap por fase temporal.
    documento.add_heading("Roadmap", level=2)
    tabla_roadmap = documento.add_table(rows=4, cols=3)
    tabla_roadmap.style = "Table Grid"
    tabla_roadmap.rows[0].cells[0].text = "Fase"
    tabla_roadmap.rows[0].cells[1].text = "Objetivo"
    tabla_roadmap.rows[0].cells[2].text = "Acciones"
    tabla_roadmap.rows[1].cells[0].text = "30 días"
    tabla_roadmap.rows[1].cells[1].text = "Estabilizar indexación"
    tabla_roadmap.rows[1].cells[2].text = "Corregir redirecciones y errores HTTP"
    tabla_roadmap.rows[2].cells[0].text = "60 días"
    tabla_roadmap.rows[2].cells[1].text = "Optimizar on-page"
    tabla_roadmap.rows[2].cells[2].text = "Completar title, H1 y meta description"
    tabla_roadmap.rows[3].cells[0].text = "90 días"
    tabla_roadmap.rows[3].cells[1].text = "Consolidar arquitectura"
    tabla_roadmap.rows[3].cells[2].text = "Alinear canonical, noindex y enlazado interno"

    # Separa bloque ejecutivo de anexo técnico.
    documento.add_page_break()

    # Añade título de anexo técnico.
    documento.add_heading("Anexo técnico", level=1)

    # Renderiza detalle técnico sin repetir narrativa ejecutiva.
    for item in resultado.resultados:
        # Añade subtítulo por URL.
        documento.add_heading(item.url, level=3)

        # Añade URL como enlace clicable.
        parrafo_url = documento.add_paragraph("URL auditada: ")
        agregar_hipervinculo(parrafo_url, item.url, "Abrir URL")

        # Añade señales técnicas básicas.
        documento.add_paragraph(f"Estado HTTP: {item.estado_http} | Redirección: {'Sí' if item.redirecciona else 'No'} | Noindex: {'Sí' if item.noindex else 'No'}")
        documento.add_paragraph(f"Title: {item.title or 'Sin title'}")
        documento.add_paragraph(f"H1: {item.h1 or 'Sin H1'}")
        documento.add_paragraph(f"Canonical: {item.canonical or 'Sin canonical'}")

        # Añade incidencias de la URL actual.
        for hallazgo in item.hallazgos:
            documento.add_paragraph(f"[{hallazgo.severidad}] {hallazgo.descripcion} -> {hallazgo.recomendacion}", style="List Bullet")

    # Guarda el documento en la ruta final.
    documento.save(destino)

    # Devuelve la ruta del archivo generado.
    return destino


# Exporta un PDF con estructura similar a Word.
def exportar_pdf(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un PDF profesional alineado con la estructura editorial del DOCX.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta final del PDF.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}.pdf"

    # Crea el documento PDF.
    pdf = SimpleDocTemplate(str(destino), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

    # Inicializa la lista de elementos de contenido.
    elementos = []

    # Obtiene estilos base de reportlab.
    estilos = getSampleStyleSheet()

    # Define estilo de subtítulo corporativo.
    estilo_subtitulo = ParagraphStyle(name="Subtitulo", parent=estilos["Normal"], fontSize=11, textColor=colors.HexColor("#5F6B73"), alignment=1)

    # Añade portada del informe con separación visual.
    elementos.append(Spacer(1, 120))
    elementos.append(Paragraph("<b>INFORME DE AUDITORÍA SEO</b>", estilos["Title"]))
    elementos.append(Spacer(1, 8))
    elementos.append(Paragraph("Auditoría técnica, de indexación y contenidos", estilo_subtitulo))
    elementos.append(Spacer(1, 18))
    elementos.append(Paragraph(f"Cliente: {sanear_texto_para_pdf(resultado.cliente)}", estilos["Normal"]))
    elementos.append(Paragraph(f"Dominio / sitemap: {sanear_texto_para_pdf(resultado.sitemap)}", estilos["Normal"]))
    elementos.append(Paragraph(f"Fecha de ejecución: {sanear_texto_para_pdf(resultado.fecha_ejecucion)}", estilos["Normal"]))
    elementos.append(Paragraph(f"Gestor: {sanear_texto_para_pdf(resultado.gestor)}", estilos["Normal"]))
    elementos.append(PageBreak())

    # Calcula métricas ejecutivas para tabla de resumen.
    metricas = calcular_metricas(resultado)

    # Añade resumen ejecutivo con tabla KPI.
    elementos.append(Paragraph("<b>Resumen ejecutivo</b>", estilos["Heading2"]))
    tabla_kpi = Table([
        ["KPI", "Valor", "KPI", "Valor"],
        ["Total URLs", str(metricas["total_urls"]), "Total incidencias", str(metricas["total_incidencias"])],
        ["URLs sanas", str(metricas["urls_sanas"]), "URLs con redirección", str(metricas["urls_redireccion"])],
        ["Score SEO", str(metricas["score"]), "Incidencias altas", str(metricas["severidades"].get("alta", 0))],
    ], colWidths=[110, 80, 130, 80])
    tabla_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (3, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (3, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9D9D9")),
    ]))
    elementos.append(tabla_kpi)
    elementos.append(Spacer(1, 12))

    # Convierte narrativa IA a secciones limpias para PDF.
    secciones_ia = construir_secciones_desde_ia(resultado.resumen_ia)

    # Renderiza contenido IA sin markdown crudo.
    for seccion in secciones_ia[:6]:
        elementos.append(Paragraph(f"<b>{sanear_texto_para_pdf(str(seccion['titulo']))}</b>", estilos["Heading3"]))
        for item in seccion["items"][:8]:
            elementos.append(Paragraph(sanear_texto_para_pdf(str(item)), estilos["Normal"]))

    # Inserta salto y anexo técnico resumido.
    elementos.append(PageBreak())
    elementos.append(Paragraph("<b>Anexo técnico</b>", estilos["Heading2"]))
    for item in resultado.resultados[:20]:
        elementos.append(Paragraph(sanear_texto_para_pdf(f"URL: {item.url}"), estilos["Normal"]))
        elementos.append(Paragraph(sanear_texto_para_pdf(f"HTTP: {item.estado_http} | Redirección: {'Sí' if item.redirecciona else 'No'} | Noindex: {'Sí' if item.noindex else 'No'}"), estilos["Normal"]))
        for hallazgo in item.hallazgos[:3]:
            elementos.append(Paragraph(sanear_texto_para_pdf(f"• [{hallazgo.severidad}] {hallazgo.descripcion}"), estilos["Normal"]))
        elementos.append(Spacer(1, 6))

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
