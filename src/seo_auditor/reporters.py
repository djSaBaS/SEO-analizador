# Importa JSON para exportar datos técnicos trazables.
import json

# Importa expresiones regulares para limpiar narrativa IA.
import re

# Importa contador para cálculos agregados.
from collections import Counter

# Importa la clase Path para gestionar rutas de forma robusta.
from pathlib import Path

# Importa escape para sanear texto potencialmente interpretado como etiquetas XML.
from xml.sax.saxutils import escape

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
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

# Importa utilidades avanzadas de maquetación PDF.
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Importa utilidades de openpyxl para Excel profesional.
from openpyxl import Workbook

# Importa gráficos de Excel.
from openpyxl.chart import BarChart, PieChart, Reference

# Importa estilos y colores de openpyxl.
from openpyxl.styles import Alignment, Font, PatternFill

# Importa validaciones de datos para celdas editables.
from openpyxl.worksheet.datavalidation import DataValidation

# Importa herramientas de tabla de openpyxl.
from openpyxl.worksheet.table import Table as ExcelTable, TableStyleInfo

# Importa los modelos del dominio del proyecto.
from seo_auditor.models import ResultadoAuditoria


# Define el orden de severidad para visualización homogénea.
ORDEN_SEVERIDAD = ["crítica", "alta", "media", "baja", "informativa"]

# Define jerarquía fija obligatoria del informe final.
JERARQUIA_INFORME = [
    "Resumen ejecutivo",
    "KPIs principales",
    "Hallazgos críticos",
    "Quick wins",
    "Acciones técnicas",
    "Acciones de contenido",
    "Rendimiento y experiencia de usuario",
    "Roadmap",
]


# Construye un prefijo de nombre de archivo legible y consistente.
def construir_prefijo_archivo(resultado: ResultadoAuditoria) -> str:
    """Genera un prefijo de naming profesional para entregables."""

    # Limpia el nombre del cliente para convertirlo en parte de archivo.
    cliente = resultado.cliente.lower().replace(" ", "_")

    # Devuelve el prefijo homogéneo de archivos exportados.
    return f"informe_seo_{cliente}_{resultado.fecha_ejecucion}"


# Sanea un texto libre para que reportlab no lo interprete como marcado inválido.
def sanear_texto_para_pdf(texto: str) -> str:
    """Limpia y escapa texto dinámico para render seguro en PDF."""

    # Normaliza saltos de línea de Windows a formato estándar.
    texto_normalizado = texto.replace("\r\n", "\n").replace("\r", "\n")

    # Escapa caracteres especiales para evitar errores del parser XML interno.
    texto_escapado = escape(texto_normalizado)

    # Devuelve texto saneado para inserción segura en PDF.
    return texto_escapado


# Limpia marcas markdown para evitar texto crudo en DOCX/PDF.
def limpiar_markdown_crudo(texto: str) -> str:
    """Elimina marcas markdown frecuentes y deja texto natural legible."""

    # Elimina separadores horizontales de markdown.
    texto_limpio = re.sub(r"^\s*---+\s*$", "", texto, flags=re.MULTILINE)

    # Elimina encabezados markdown conservando el contenido.
    texto_limpio = re.sub(r"^\s*#{1,6}\s*", "", texto_limpio, flags=re.MULTILINE)

    # Elimina negritas y cursivas markdown.
    texto_limpio = texto_limpio.replace("**", "").replace("__", "")

    # Elimina bloques de código en línea.
    texto_limpio = texto_limpio.replace("`", "")

    # Devuelve el texto con limpieza por línea.
    return "\n".join(linea.strip() for linea in texto_limpio.splitlines())


# Convierte narrativa IA en secciones internas estructuradas.
def construir_secciones_desde_ia(texto_ia: str | None) -> list[dict[str, object]]:
    """Transforma texto IA en secciones semánticas sin markdown crudo."""

    # Devuelve colección vacía cuando no exista contenido IA.
    if not texto_ia:
        # Retorna una lista vacía para simplificar flujo.
        return []

    # Limpia markdown para evitar arrastre en entregables.
    texto_limpio = limpiar_markdown_crudo(texto_ia)

    # Inicializa resultado de secciones intermedias.
    secciones: list[dict[str, object]] = []

    # Inicializa sección por defecto de arranque.
    seccion_actual: dict[str, object] = {"titulo": "Resumen ejecutivo", "tipo": "parrafos", "items": []}

    # Recorre líneas del texto limpio.
    for linea in texto_limpio.splitlines():
        # Descarta líneas vacías.
        if not linea.strip():
            # Continúa con la siguiente línea útil.
            continue

        # Detecta títulos de sección de forma tolerante.
        if re.match(r"^(\d+[\).]\s*)?(resumen|kpis|hallazgos|quick wins|acciones técnicas|acciones de contenido|rendimiento|roadmap)", linea.lower()):
            # Guarda sección previa cuando tenga contenido.
            if seccion_actual["items"]:
                # Inserta sección construida en la lista final.
                secciones.append(seccion_actual)

            # Limpia numeración inicial del título.
            titulo = re.sub(r"^\d+[\).]\s*", "", linea).strip().title()

            # Crea nueva sección activa.
            seccion_actual = {"titulo": titulo, "tipo": "parrafos", "items": []}

            # Continúa sin añadir la línea como contenido.
            continue

        # Detecta viñetas con prefijos habituales.
        if linea.startswith(("- ", "* ", "• ")):
            # Cambia tipo de sección a viñetas.
            seccion_actual["tipo"] = "vinetas"

            # Añade item sin el prefijo de viñeta.
            seccion_actual["items"].append(linea[2:].strip())

            # Continúa con la siguiente línea.
            continue

        # Detecta listas numeradas y las normaliza.
        if re.match(r"^\d+[\).]\s+", linea):
            # Cambia tipo de sección a lista numerada.
            seccion_actual["tipo"] = "numerada"

            # Añade item eliminando el prefijo numérico.
            seccion_actual["items"].append(re.sub(r"^\d+[\).]\s*", "", linea).strip())

            # Continúa con la siguiente línea.
            continue

        # Añade línea como párrafo normal.
        seccion_actual["items"].append(linea.strip())

    # Añade última sección pendiente si tiene contenido.
    if seccion_actual["items"]:
        # Inserta sección final en la colección.
        secciones.append(seccion_actual)

    # Devuelve secciones intermedias para renderizado estable.
    return secciones


# Convierte el resultado a una estructura tabular cómoda para exportación.
def construir_filas(resultado: ResultadoAuditoria) -> list[dict]:
    """Convierte el resultado de auditoría a una lista de filas tabulares."""

    # Inicializa la colección de filas tabulares.
    filas: list[dict] = []

    # Recorre cada URL auditada para convertirla a filas de incidencias.
    for item in resultado.resultados:
        # Construye una base común para evitar duplicación de campos.
        fila_base = {
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
            "estado": "Pendiente",
            "resuelto": "No",
            "responsable": "",
        }

        # Inserta fila de control cuando no haya hallazgos.
        if not item.hallazgos:
            # Crea copia independiente de la fila base.
            fila = fila_base.copy()

            # Completa datos por defecto para URL sin incidencias.
            fila.update({"problema": "", "recomendacion": "", "severidad": "informativa", "area": "Calidad", "impacto": "Bajo", "esfuerzo": "Bajo", "prioridad": "P4", "observaciones": item.error or "Sin incidencias críticas"})

            # Añade fila informativa final a la colección.
            filas.append(fila)

        # Recorre hallazgos cuando existan para crear filas detalladas.
        for hallazgo in item.hallazgos:
            # Crea copia independiente de la fila base.
            fila = fila_base.copy()

            # Completa datos de hallazgo para esta fila.
            fila.update({"problema": hallazgo.descripcion, "recomendacion": hallazgo.recomendacion, "severidad": hallazgo.severidad, "area": hallazgo.area, "impacto": hallazgo.impacto, "esfuerzo": hallazgo.esfuerzo, "prioridad": hallazgo.prioridad, "observaciones": item.error or ""})

            # Añade una fila por hallazgo detectado.
            filas.append(fila)

    # Devuelve las filas preparadas para cualquier exportador.
    return filas


# Convierte resultados de PageSpeed a filas de seguimiento.
def construir_filas_rendimiento(resultado: ResultadoAuditoria) -> list[dict]:
    """Construye filas para hoja Rendimiento y anexo técnico de performance."""

    # Inicializa lista de filas de rendimiento.
    filas: list[dict] = []

    # Recorre cada resultado de PageSpeed disponible.
    for item in resultado.rendimiento:
        # Construye una base común para evitar duplicación de campos.
        fila_base = {
            "url": item.url,
            "estrategia": item.estrategia,
            "performance_score": item.performance_score,
            "accessibility_score": item.accessibility_score,
            "best_practices_score": item.best_practices_score,
            "seo_score": item.seo_score,
            "lcp": item.lcp,
            "cls": item.cls,
            "inp": item.inp,
            "fcp": item.fcp,
            "speed_index": item.speed_index,
            "estado": "Pendiente",
            "resuelto": "No",
            "responsable": "",
        }

        # Crea una fila base cuando no haya oportunidades.
        if not item.oportunidades:
            # Crea copia independiente de la fila base.
            fila = fila_base.copy()

            # Completa datos por defecto para esta ejecución.
            fila.update({"oportunidad": "", "descripcion": item.error or "Sin oportunidades destacadas", "ahorro_estimado": "", "severidad": "informativa", "recomendacion": "Mantener monitorización continua", "observaciones": item.error or ""})

            # Añade fila base de métricas sin oportunidad concreta.
            filas.append(fila)

        # Recorre oportunidades para crear filas accionables.
        for oportunidad in item.oportunidades:
            # Crea copia independiente de la fila base.
            fila = fila_base.copy()

            # Completa datos específicos de la oportunidad.
            fila.update({"oportunidad": oportunidad.titulo, "descripcion": oportunidad.descripcion, "ahorro_estimado": oportunidad.ahorro_estimado, "severidad": oportunidad.severidad, "recomendacion": f"Aplicar mejora: {oportunidad.titulo}", "observaciones": ""})

            # Añade fila por oportunidad detectada.
            filas.append(fila)

    # Devuelve filas listas para Excel.
    return filas


# Garantiza que la carpeta de salida exista antes de escribir archivos.
def asegurar_directorio(path_salida: Path) -> None:
    """Crea la carpeta de salida si no existe."""

    # Crea el directorio y sus padres sin fallar si ya existen.
    path_salida.mkdir(parents=True, exist_ok=True)


# Calcula métricas ejecutivas agregadas para informes.
def calcular_metricas(resultado: ResultadoAuditoria) -> dict[str, int | float | dict[str, int] | str]:
    """Calcula métricas ejecutivas reutilizables por todos los reportes."""

    # Inicializa acumuladores principales.
    total_incidencias = 0

    # Inicializa contadores de URLs.
    urls_sanas = 0

    # Inicializa distribución por severidad.
    severidades: Counter[str] = Counter()

    # Inicializa distribución por tipo.
    tipos: Counter[str] = Counter()

    # Inicializa distribución por área.
    areas: Counter[str] = Counter()

    # Recorre resultados para consolidar datos.
    for item in resultado.resultados:
        # Suma incidencias de la URL actual.
        total_incidencias += len(item.hallazgos)

        # Cuenta URL sana cuando no hay hallazgos.
        if not item.hallazgos:
            # Incrementa contador de URLs sin incidencias.
            urls_sanas += 1

        # Recorre hallazgos para completar distribuciones.
        for hallazgo in item.hallazgos:
            # Incrementa la severidad detectada.
            severidades[hallazgo.severidad] += 1

            # Incrementa el tipo detectado.
            tipos[hallazgo.tipo] += 1

            # Incrementa el área detectada.
            areas[hallazgo.area] += 1

    # Define pesos de scoring por severidad.
    pesos = {"crítica": 10.0, "alta": 6.0, "media": 3.0, "baja": 1.0, "informativa": 0.5}

    # Calcula penalización ponderada total.
    penalizacion = sum(severidades.get(severidad, 0) * peso for severidad, peso in pesos.items())

    # Calcula máximo teórico por volumen auditado.
    max_penalizacion = max(10.0, float(resultado.total_urls) * 10.0)

    # Calcula score SEO global acotado entre 5 y 100.
    score = round(max(5.0, min(100.0, 100.0 - (penalizacion / max_penalizacion) * 100.0)), 1)

    # Devuelve métricas calculadas.
    return {"total_urls": resultado.total_urls, "total_incidencias": total_incidencias, "severidades": dict(severidades), "tipos": dict(tipos), "areas": dict(areas), "urls_sanas": urls_sanas, "score": score, "formula_score": "Score = 100 - (penalización_ponderada/(total_urls*10))*100"}


# Construye la narrativa final sin duplicar secciones.
def _construir_bloques_narrativos(resultado: ResultadoAuditoria) -> dict[str, list[str]]:
    """Genera bloques narrativos únicos siguiendo jerarquía editorial obligatoria."""

    # Construye diccionario base con todas las secciones requeridas.
    bloques = {titulo: [] for titulo in JERARQUIA_INFORME}

    # Obtiene secciones procesadas desde IA cuando existan.
    secciones_ia = construir_secciones_desde_ia(resultado.resumen_ia)

    # Recorre secciones IA para mapearlas a la jerarquía interna.
    for seccion in secciones_ia:
        # Obtiene título normalizado de sección.
        titulo = str(seccion["titulo"]).strip().lower()

        # Recorre jerarquía para encontrar destino compatible.
        for destino in JERARQUIA_INFORME:
            # Compara por inclusión simple para robustez.
            if destino.lower() in titulo or titulo in destino.lower():
                # Inserta solo textos no vacíos en el bloque destino.
                bloques[destino].extend([str(item).strip() for item in seccion["items"] if str(item).strip()])

    # Construye vistas tabulares para generar fallback de secciones obligatorias.
    filas = construir_filas(resultado)

    # Construye vista tabular de rendimiento para secciones de UX.
    filas_rendimiento = construir_filas_rendimiento(resultado)

    # Construye fallback de resumen ejecutivo cuando IA no aporta contenido.
    if not bloques["Resumen ejecutivo"]:
        # Añade resumen automático con datos técnicos.
        bloques["Resumen ejecutivo"].append(f"Se auditaron {resultado.total_urls} URLs con fuentes activas: {', '.join(resultado.fuentes_activas)}.")

    # Construye fallback de KPIs principales para mantener consistencia de jerarquía.
    if not bloques["KPIs principales"]:
        # Añade recordatorio de que los KPIs se muestran en tabla.
        bloques["KPIs principales"].append("Los indicadores clave se presentan en la tabla KPI de esta sección.")

    # Construye fallback de hallazgos críticos cuando no exista IA útil.
    if not bloques["Hallazgos críticos"]:
        # Filtra hallazgos críticos para el bloque ejecutivo.
        hallazgos_criticos = [fila for fila in filas if str(fila.get("severidad", "")).lower() in {"crítica", "alta"} and fila.get("problema")]

        # Inserta resumen compacto de hallazgos prioritarios.
        for fila in hallazgos_criticos[:5]:
            # Añade línea ejecutiva de hallazgo.
            bloques["Hallazgos críticos"].append(f"[{fila['severidad']}] {fila['problema']} ({fila['url']})")

    # Construye fallback de quick wins cuando no exista narrativa IA.
    if not bloques["Quick wins"]:
        # Filtra acciones de bajo esfuerzo y alto impacto.
        quick_wins = [fila for fila in filas if fila.get("esfuerzo") == "Bajo" and fila.get("impacto") in {"Muy alto", "Alto", "Medio"} and fila.get("recomendacion")]

        # Inserta recomendaciones rápidas priorizadas.
        for fila in quick_wins[:5]:
            # Añade quick win concreto.
            bloques["Quick wins"].append(f"{fila['recomendacion']} ({fila['url']})")

    # Construye fallback de acciones técnicas cuando no haya bloque IA.
    if not bloques["Acciones técnicas"]:
        # Filtra recomendaciones técnicas.
        acciones_tecnicas = [fila for fila in filas if fila.get("area") in {"Infraestructura", "Indexación", "Arquitectura"} and fila.get("recomendacion")]

        # Inserta recomendaciones técnicas de mayor prioridad.
        for fila in acciones_tecnicas[:5]:
            # Añade acción técnica priorizada.
            bloques["Acciones técnicas"].append(f"{fila['prioridad']}: {fila['recomendacion']}")

        # Añade fallback genérico cuando no existan acciones técnicas específicas.
        if not bloques["Acciones técnicas"]:
            # Inserta recomendación de revisión técnica base.
            bloques["Acciones técnicas"].append("Revisar cobertura de rastreo, estado HTTP y canonicals para mantener estabilidad técnica.")

    # Construye fallback de acciones de contenido cuando no haya bloque IA.
    if not bloques["Acciones de contenido"]:
        # Filtra recomendaciones del área de contenido.
        acciones_contenido = [fila for fila in filas if fila.get("area") == "Contenido" and fila.get("recomendacion")]

        # Inserta recomendaciones editoriales de mayor prioridad.
        for fila in acciones_contenido[:5]:
            # Añade acción de contenido priorizada.
            bloques["Acciones de contenido"].append(f"{fila['prioridad']}: {fila['recomendacion']}")

    # Construye fallback de rendimiento y experiencia de usuario.
    if not bloques["Rendimiento y experiencia de usuario"]:
        # Inserta resumen de PageSpeed cuando exista información.
        for fila in filas_rendimiento[:5]:
            # Añade línea compacta con score y oportunidad.
            bloques["Rendimiento y experiencia de usuario"].append(f"{fila['url']} [{fila['estrategia']}] score={fila['performance_score']} oportunidad={fila['oportunidad'] or 'sin oportunidad destacada'}")

        # Añade mensaje neutro cuando no hay datos de rendimiento.
        if not bloques["Rendimiento y experiencia de usuario"]:
            # Inserta texto de continuidad operativa.
            bloques["Rendimiento y experiencia de usuario"].append("No se han recibido datos de PageSpeed en esta ejecución.")

    # Construye fallback de roadmap cuando IA no lo entregue.
    if not bloques["Roadmap"]:
        # Añade fase corta de estabilización.
        bloques["Roadmap"].append("30 días: corregir incidencias críticas y altas de indexación e infraestructura.")
        # Añade fase media de optimización.
        bloques["Roadmap"].append("60 días: ejecutar quick wins y completar mejoras on-page.")
        # Añade fase de consolidación.
        bloques["Roadmap"].append("90 días: consolidar rendimiento, calidad de contenido y control SEO continuo.")

    # Devuelve bloques listos para render narrativo.
    return bloques


# Exporta el resultado técnico en formato JSON.
def exportar_json(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Genera un JSON técnico con todos los resultados y metadatos."""

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo JSON técnico.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}_tecnico.json"

    # Construye contenido serializable completo.
    contenido = {
        "sitemap": resultado.sitemap,
        "cliente": resultado.cliente,
        "gestor": resultado.gestor,
        "fecha_ejecucion": resultado.fecha_ejecucion,
        "fuentes_activas": resultado.fuentes_activas,
        "total_urls": resultado.total_urls,
        "resumen_ia": resultado.resumen_ia,
        "metricas": calcular_metricas(resultado),
        "resultados": construir_filas(resultado),
        "rendimiento": construir_filas_rendimiento(resultado),
    }

    # Escribe el JSON con codificación UTF-8 legible.
    destino.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")

    # Devuelve la ruta final del archivo generado.
    return destino


# Exporta el detalle tabular a Excel.
def exportar_excel(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Genera un Excel profesional con dashboard, hoja de errores y hoja de rendimiento."""

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo Excel final.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}.xlsx"

    # Crea libro de trabajo.
    libro = Workbook()

    # Prepara hoja dashboard.
    hoja_dashboard = libro.active

    # Renombra hoja principal.
    hoja_dashboard.title = "Dashboard"

    # Crea hojas auxiliares de trabajo.
    hoja_errores = libro.create_sheet("Errores")

    # Crea hoja específica de rendimiento.
    hoja_rendimiento = libro.create_sheet("Rendimiento")

    # Construye filas técnicas y de rendimiento.
    filas = construir_filas(resultado)

    # Construye filas de rendimiento.
    filas_rendimiento = construir_filas_rendimiento(resultado)

    # Escribe tabla de errores.
    encabezados = list(filas[0].keys()) if filas else []

    # Recorre encabezados de errores.
    for columna, encabezado in enumerate(encabezados, start=1):
        # Escribe cada encabezado.
        hoja_errores.cell(row=1, column=columna, value=encabezado)

    # Escribe contenido de errores.
    for fila_indice, fila in enumerate(filas, start=2):
        # Recorre columnas de la fila.
        for columna, encabezado in enumerate(encabezados, start=1):
            # Escribe valor de celda.
            hoja_errores.cell(row=fila_indice, column=columna, value=fila[encabezado])

    # Aplica formato básico de encabezado en errores.
    for celda in hoja_errores[1]:
        # Define estilo de encabezado.
        celda.font = Font(bold=True, color="FFFFFF")

        # Aplica color corporativo.
        celda.fill = PatternFill(fill_type="solid", fgColor="1F4E78")

    # Configura ancho y ajuste de texto en errores.
    for columna in "ABCDEFGHIJKLMNOPQRSTU":
        # Establece ancho cómodo por defecto.
        hoja_errores.column_dimensions[columna].width = 24

    # Ajusta celdas para legibilidad.
    for fila in hoja_errores.iter_rows(min_row=2, max_row=max(2, len(filas) + 1), min_col=1, max_col=max(1, len(encabezados))):
        # Recorre celdas de la fila.
        for celda in fila:
            # Activa ajuste automático de texto.
            celda.alignment = Alignment(wrap_text=True, vertical="top")

    # Aplica validación de datos Sí/No en columna resuelto.
    validacion_resuelto = DataValidation(type="list", formula1='"Sí,No"', allow_blank=False)

    # Registra validación en hoja.
    hoja_errores.add_data_validation(validacion_resuelto)

    # Aplica validación al rango de seguimiento.
    validacion_resuelto.add(f"S2:S{max(2, len(filas) + 1)}")

    # Escribe tabla de rendimiento con esquema obligatorio.
    columnas_rendimiento = ["url", "estrategia", "performance_score", "accessibility_score", "best_practices_score", "seo_score", "lcp", "cls", "inp", "fcp", "speed_index", "oportunidad", "descripcion", "ahorro_estimado", "severidad", "recomendacion", "estado", "resuelto", "responsable", "observaciones"]

    # Recorre encabezados de rendimiento.
    for columna, encabezado in enumerate(columnas_rendimiento, start=1):
        # Escribe encabezado en hoja de rendimiento.
        hoja_rendimiento.cell(row=1, column=columna, value=encabezado)

    # Recorre filas de rendimiento para poblar hoja.
    for fila_indice, fila in enumerate(filas_rendimiento, start=2):
        # Recorre columnas obligatorias.
        for columna, encabezado in enumerate(columnas_rendimiento, start=1):
            # Escribe valor de columna o vacío por defecto.
            hoja_rendimiento.cell(row=fila_indice, column=columna, value=fila.get(encabezado, ""))

    # Estiliza encabezado de rendimiento.
    for celda in hoja_rendimiento[1]:
        # Define negrita de encabezado.
        celda.font = Font(bold=True, color="FFFFFF")

        # Aplica fondo corporativo.
        celda.fill = PatternFill(fill_type="solid", fgColor="1F4E78")

    # Ajusta lectura de hoja rendimiento.
    for indice in range(1, len(columnas_rendimiento) + 1):
        # Asigna ancho homogéneo por columna.
        hoja_rendimiento.column_dimensions[chr(64 + indice)].width = 22

    # Activa wrap y alineación superior en rendimiento.
    for fila in hoja_rendimiento.iter_rows(min_row=2, max_row=max(2, len(filas_rendimiento) + 1), min_col=1, max_col=len(columnas_rendimiento)):
        # Recorre celdas de fila.
        for celda in fila:
            # Configura alineación legible.
            celda.alignment = Alignment(wrap_text=True, vertical="top")

    # Calcula métricas de dashboard.
    metricas = calcular_metricas(resultado)

    # Calcula scores medios mobile y desktop desde ejecuciones únicas.
    scores_mobile = [item.performance_score for item in resultado.rendimiento if item.estrategia == "mobile" and isinstance(item.performance_score, (int, float))]

    # Calcula scores de desktop desde ejecuciones únicas.
    scores_desktop = [item.performance_score for item in resultado.rendimiento if item.estrategia == "desktop" and isinstance(item.performance_score, (int, float))]

    # Obtiene media mobile segura.
    score_medio_mobile = round(sum(scores_mobile) / len(scores_mobile), 1) if scores_mobile else 0.0

    # Obtiene media desktop segura.
    score_medio_desktop = round(sum(scores_desktop) / len(scores_desktop), 1) if scores_desktop else 0.0

    # Define KPIs del dashboard.
    hoja_dashboard["A1"] = "Dashboard SEO"

    # Aplica estilo de título.
    hoja_dashboard["A1"].font = Font(size=18, bold=True, color="1F4E78")

    # Escribe tarjeta de URLs.
    hoja_dashboard["A3"] = "Total URLs"

    # Escribe valor de URLs.
    hoja_dashboard["B3"] = metricas["total_urls"]

    # Escribe tarjeta de incidencias.
    hoja_dashboard["A4"] = "Total incidencias"

    # Escribe valor de incidencias.
    hoja_dashboard["B4"] = metricas["total_incidencias"]

    # Escribe score medio móvil.
    hoja_dashboard["A5"] = "Score medio móvil"

    # Escribe valor de score móvil.
    hoja_dashboard["B5"] = score_medio_mobile

    # Escribe score medio escritorio.
    hoja_dashboard["A6"] = "Score medio escritorio"

    # Escribe valor de score escritorio.
    hoja_dashboard["B6"] = score_medio_desktop

    # Escribe total de oportunidades.
    hoja_dashboard["A7"] = "Total oportunidades"

    # Escribe conteo de oportunidades.
    hoja_dashboard["B7"] = len([fila for fila in filas_rendimiento if fila.get("oportunidad")])

    # Prepara tabla auxiliar para gráfico por severidad de rendimiento.
    severidades_rend = Counter([str(fila.get("severidad", "informativa")).lower() for fila in filas_rendimiento])

    # Escribe cabecera auxiliar.
    hoja_dashboard["D3"] = "Severidad"

    # Escribe cabecera auxiliar de cantidad.
    hoja_dashboard["E3"] = "Cantidad"

    # Recorre severidades estándar.
    for indice, severidad in enumerate(["crítica", "alta", "media", "baja", "informativa"], start=4):
        # Escribe nombre de severidad.
        hoja_dashboard[f"D{indice}"] = severidad

        # Escribe cantidad asociada.
        hoja_dashboard[f"E{indice}"] = severidades_rend.get(severidad, 0)

    # Crea gráfico de distribución de severidad.
    grafico_severidad = PieChart()

    # Define título del gráfico.
    grafico_severidad.title = "Distribución oportunidades por severidad"

    # Carga datos del gráfico.
    grafico_severidad.add_data(Reference(hoja_dashboard, min_col=5, min_row=3, max_row=8), titles_from_data=True)

    # Carga categorías del gráfico.
    grafico_severidad.set_categories(Reference(hoja_dashboard, min_col=4, min_row=4, max_row=8))

    # Fija tamaño visual del gráfico.
    grafico_severidad.width = 8

    # Fija altura visual del gráfico.
    grafico_severidad.height = 6

    # Inserta gráfico en posición explícita.
    hoja_dashboard.add_chart(grafico_severidad, "G3")

    # Crea tabla Excel en hoja rendimiento cuando haya filas.
    if filas_rendimiento:
        # Define rango dinámico de tabla de rendimiento.
        rango = f"A1:T{len(filas_rendimiento) + 1}"

        # Crea tabla de rendimiento.
        tabla = ExcelTable(displayName="TablaRendimiento", ref=rango)

        # Define estilo de tabla.
        tabla.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)

        # Inserta tabla en hoja.
        hoja_rendimiento.add_table(tabla)

    # Guarda libro final en disco.
    libro.save(destino)

    # Devuelve ruta de salida.
    return destino


# Exporta un informe ejecutivo en Word.
def exportar_word(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Genera un DOCX corporativo usando estructura semántica intermedia."""

    # Garantiza carpeta de salida.
    asegurar_directorio(path_salida)

    # Define ruta del documento Word.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}.docx"

    # Crea documento vacío.
    documento = Document()

    # Configura estilo base de documento.
    documento.styles["Normal"].font.name = "Calibri"

    # Configura tamaño base de fuente.
    documento.styles["Normal"].font.size = Pt(11)

    # Inserta portada.
    titulo = documento.add_paragraph("INFORME DE AUDITORÍA SEO")

    # Centra título de portada.
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Aplica estilo visual a portada.
    titulo.runs[0].font.color.rgb = RGBColor(31, 78, 120)

    # Aplica tamaño destacado a portada.
    titulo.runs[0].font.size = Pt(26)

    # Añade metadatos de portada.
    documento.add_paragraph(f"Cliente: {resultado.cliente}")

    # Añade metadatos de sitemap.
    documento.add_paragraph(f"Sitemap: {resultado.sitemap}")

    # Añade metadatos de fecha.
    documento.add_paragraph(f"Fecha: {resultado.fecha_ejecucion}")

    # Inserta salto de página tras portada.
    documento.add_page_break()

    # Obtiene métricas para bloque KPI.
    metricas = calcular_metricas(resultado)

    # Construye bloques narrativos sin duplicidades.
    bloques = _construir_bloques_narrativos(resultado)

    # Renderiza jerarquía fija en orden obligatorio.
    for titulo_seccion in JERARQUIA_INFORME:
        # Inserta encabezado de sección.
        documento.add_heading(titulo_seccion, level=1)

        # Inserta tabla de KPI en su sección dedicada.
        if titulo_seccion == "KPIs principales":
            # Crea tabla KPI de dos columnas.
            tabla = documento.add_table(rows=4, cols=2)

            # Aplica estilo de tabla.
            tabla.style = "Table Grid"

            # Completa filas de KPI.
            tabla.cell(0, 0).text = "Total URLs"
            tabla.cell(0, 1).text = str(metricas["total_urls"])
            tabla.cell(1, 0).text = "Total incidencias"
            tabla.cell(1, 1).text = str(metricas["total_incidencias"])
            tabla.cell(2, 0).text = "Score SEO"
            tabla.cell(2, 1).text = str(metricas["score"])
            tabla.cell(3, 0).text = "Fuentes activas"
            tabla.cell(3, 1).text = ", ".join(resultado.fuentes_activas)

            # Continúa con siguiente sección.
            continue

        # Inserta bloque específico de rendimiento.
        if titulo_seccion == "Rendimiento y experiencia de usuario":
            # Recorre resultados de rendimiento resumidos.
            for item in resultado.rendimiento[:8]:
                # Inserta párrafo de métricas clave por estrategia.
                documento.add_paragraph(f"{item.url} [{item.estrategia}] · performance={item.performance_score} · seo={item.seo_score} · LCP={item.lcp} · CLS={item.cls} · INP={item.inp}")

            # Continúa con siguiente sección.
            continue

        # Inserta narrativa no vacía de la sección.
        for linea in bloques[titulo_seccion][:8]:
            # Añade párrafo limpio sin markdown crudo.
            documento.add_paragraph(linea)

    # Inserta anexo técnico como sección única al final.
    documento.add_page_break()

    # Inserta encabezado de anexo.
    documento.add_heading("Anexo técnico", level=1)

    # Recorre una muestra de URLs para anexo estructurado.
    for item in resultado.resultados[:20]:
        # Inserta subtítulo por URL.
        documento.add_heading(item.url, level=2)

        # Inserta línea de estado técnico.
        documento.add_paragraph(f"HTTP={item.estado_http} · redirección={'Sí' if item.redirecciona else 'No'} · noindex={'Sí' if item.noindex else 'No'}")

        # Recorre hallazgos de la URL.
        for hallazgo in item.hallazgos[:3]:
            # Añade hallazgo en formato de lista.
            documento.add_paragraph(f"[{hallazgo.severidad}] {hallazgo.descripcion}", style="List Bullet")

    # Guarda documento final.
    documento.save(destino)

    # Devuelve ruta del Word generado.
    return destino


# Exporta un PDF con estructura similar a Word.
def exportar_pdf(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """Genera un PDF profesional respetando la misma jerarquía documental."""

    # Garantiza carpeta de salida.
    asegurar_directorio(path_salida)

    # Define ruta del PDF final.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}.pdf"

    # Crea documento PDF base.
    pdf = SimpleDocTemplate(str(destino), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

    # Inicializa lista de elementos del PDF.
    elementos = []

    # Obtiene estilos de referencia.
    estilos = getSampleStyleSheet()

    # Crea estilo de portada.
    estilo_portada = ParagraphStyle(name="Portada", parent=estilos["Title"], alignment=1, textColor=colors.HexColor("#1F4E78"))

    # Inserta portada.
    elementos.append(Spacer(1, 80))

    # Inserta título de portada.
    elementos.append(Paragraph("INFORME DE AUDITORÍA SEO", estilo_portada))

    # Inserta datos generales de portada.
    elementos.append(Spacer(1, 16))
    elementos.append(Paragraph(f"Cliente: {sanear_texto_para_pdf(resultado.cliente)}", estilos["Normal"]))
    elementos.append(Paragraph(f"Sitemap: {sanear_texto_para_pdf(resultado.sitemap)}", estilos["Normal"]))
    elementos.append(PageBreak())

    # Obtiene bloques narrativos consolidados.
    bloques = _construir_bloques_narrativos(resultado)

    # Obtiene métricas globales.
    metricas = calcular_metricas(resultado)

    # Recorre jerarquía del informe.
    for titulo_seccion in JERARQUIA_INFORME:
        # Inserta título de sección.
        elementos.append(Paragraph(f"<b>{sanear_texto_para_pdf(titulo_seccion)}</b>", estilos["Heading2"]))

        # Inserta tabla KPI en sección correspondiente.
        if titulo_seccion == "KPIs principales":
            # Crea tabla de KPIs.
            tabla = Table([["KPI", "Valor"], ["Total URLs", str(metricas["total_urls"])], ["Total incidencias", str(metricas["total_incidencias"])], ["Score SEO", str(metricas["score"])], ["Fuentes activas", ", ".join(resultado.fuentes_activas)]], colWidths=[180, 280])

            # Aplica estilo visual de tabla.
            tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#1F4E78")), ("TEXTCOLOR", (0, 0), (1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9D9D9"))]))

            # Añade tabla al flujo.
            elementos.append(tabla)

            # Salta a siguiente sección.
            continue

        # Inserta resumen de rendimiento.
        if titulo_seccion == "Rendimiento y experiencia de usuario":
            # Recorre resultados de rendimiento.
            for item in resultado.rendimiento[:8]:
                # Inserta línea de métricas clave.
                elementos.append(Paragraph(sanear_texto_para_pdf(f"{item.url} [{item.estrategia}] performance={item.performance_score} seo={item.seo_score} LCP={item.lcp} CLS={item.cls} INP={item.inp}"), estilos["Normal"]))

            # Salta a siguiente sección.
            continue

        # Inserta líneas narrativas de sección.
        for linea in bloques[titulo_seccion][:8]:
            # Añade párrafo saneado.
            elementos.append(Paragraph(sanear_texto_para_pdf(linea), estilos["Normal"]))

        # Añade espacio vertical entre secciones.
        elementos.append(Spacer(1, 6))

    # Inserta anexo técnico al final.
    elementos.append(PageBreak())

    # Inserta título de anexo.
    elementos.append(Paragraph("<b>Anexo técnico</b>", estilos["Heading2"]))

    # Recorre muestra de URLs para el anexo.
    for item in resultado.resultados[:20]:
        # Inserta encabezado por URL.
        elementos.append(Paragraph(sanear_texto_para_pdf(item.url), estilos["Heading3"]))

        # Inserta estado base de la URL.
        elementos.append(Paragraph(sanear_texto_para_pdf(f"HTTP={item.estado_http} · redirección={'Sí' if item.redirecciona else 'No'} · noindex={'Sí' if item.noindex else 'No'}"), estilos["Normal"]))

    # Construye PDF final.
    pdf.build(elementos)

    # Devuelve ruta del PDF generado.
    return destino


# Exporta el informe IA en Markdown para edición y revisión humana.
def exportar_markdown_ia(resultado: ResultadoAuditoria, path_salida: Path) -> Path | None:
    """Genera un archivo Markdown con el resumen IA y metadatos."""

    # Sale sin crear archivo cuando no existe resumen IA.
    if not resultado.resumen_ia:
        # Retorna None cuando no hay contenido IA.
        return None

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo Markdown.
    destino = path_salida / f"{construir_prefijo_archivo(resultado)}_ia.md"

    # Construye encabezado contextual de informe.
    contenido = f"# Informe SEO IA\n\n- Cliente: {resultado.cliente}\n- Gestor: {resultado.gestor}\n- Fecha de ejecución: {resultado.fecha_ejecucion}\n- Sitemap: {resultado.sitemap}\n\n{resultado.resumen_ia}\n"

    # Escribe el contenido del informe IA en UTF-8.
    destino.write_text(contenido, encoding="utf-8")

    # Devuelve la ruta del archivo generado.
    return destino
