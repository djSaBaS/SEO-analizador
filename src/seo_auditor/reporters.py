# Importa JSON para exportar datos técnicos trazables.
import json

# Importa la clase Path para gestionar rutas de forma robusta.
from pathlib import Path

# Importa pandas para generar el Excel profesional.
import pandas as pd

# Importa utilidades de Word para crear informes DOCX.
from docx import Document

# Importa utilidades de PDF para generar un informe simple portable.
from reportlab.lib.pagesizes import A4

# Importa utilidades básicas de dibujo del PDF.
from reportlab.pdfgen import canvas

# Importa los modelos del dominio del proyecto.
from seo_auditor.models import ResultadoAuditoria


# Convierte el resultado a una estructura tabular cómoda para exportación.
def construir_filas(resultado: ResultadoAuditoria) -> list[dict]:
    """
    Convierte el resultado de auditoría a una lista de filas tabulares.

    Parameters
    ----------
    resultado : ResultadoAuditoria
        Resultado global de la auditoría.

    Returns
    -------
    list[dict]
        Filas listas para convertir a DataFrame o JSON.
    """

    # Inicializa la colección de filas tabulares.
    filas: list[dict] = []

    # Recorre cada URL auditada para convertirla a una fila plana.
    for item in resultado.resultados:
        # Concatena descripciones de hallazgos para vista ejecutiva.
        problemas = " | ".join(h.descripcion for h in item.hallazgos)

        # Concatena recomendaciones para facilitar la revisión en Excel.
        recomendaciones = " | ".join(h.recomendacion for h in item.hallazgos)

        # Añade una fila con los campos clave de auditoría.
        filas.append(
            {
                # Guarda la URL auditada.
                "url": item.url,
                # Guarda el tipo lógico de URL.
                "tipo": item.tipo,
                # Guarda el código HTTP final.
                "estado_http": item.estado_http,
                # Guarda si hubo redirección.
                "redirecciona": item.redirecciona,
                # Guarda la URL final resuelta.
                "url_final": item.url_final,
                # Guarda el title observado.
                "title": item.title,
                # Guarda el H1 observado.
                "h1": item.h1,
                # Guarda la meta description observada.
                "meta_description": item.meta_description,
                # Guarda la canonical observada.
                "canonical": item.canonical or "",
                # Guarda la directiva noindex.
                "noindex": item.noindex,
                # Guarda el resumen de problemas detectados.
                "problemas": problemas,
                # Guarda el resumen de acciones recomendadas.
                "recomendaciones": recomendaciones,
                # Guarda un eventual error controlado.
                "error": item.error or "",
            }
        )

    # Devuelve las filas preparadas para cualquier exportador.
    return filas


# Garantiza que la carpeta de salida exista antes de escribir archivos.
def asegurar_directorio(path_salida: Path) -> None:
    """
    Crea la carpeta de salida si no existe.

    Parameters
    ----------
    path_salida : Path
        Directorio objetivo.
    """

    # Crea el directorio y sus padres sin fallar si ya existen.
    path_salida.mkdir(parents=True, exist_ok=True)


# Exporta el resultado técnico en formato JSON.
def exportar_json(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un JSON técnico con todos los resultados.

    Parameters
    ----------
    resultado : ResultadoAuditoria
        Resultado de la auditoría.
    path_salida : Path
        Carpeta destino.

    Returns
    -------
    Path
        Ruta del archivo generado.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo JSON técnico.
    destino = path_salida / "resultado_tecnico.json"

    # Construye un diccionario serializable con todos los resultados.
    contenido = {
        # Expone el sitemap auditado.
        "sitemap": resultado.sitemap,
        # Expone el total de URLs procesadas.
        "total_urls": resultado.total_urls,
        # Expone el resumen IA si existe.
        "resumen_ia": resultado.resumen_ia,
        # Expone las filas tabulares del resultado.
        "resultados": construir_filas(resultado),
    }

    # Escribe el JSON con codificación UTF-8 legible.
    destino.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")

    # Devuelve la ruta final del archivo generado.
    return destino


# Exporta el detalle tabular a Excel.
def exportar_excel(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un Excel con el detalle de URLs auditadas.

    Parameters
    ----------
    resultado : ResultadoAuditoria
        Resultado de la auditoría.
    path_salida : Path
        Carpeta destino.

    Returns
    -------
    Path
        Ruta del archivo generado.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo Excel final.
    destino = path_salida / "urls_auditadas.xlsx"

    # Convierte las filas a un DataFrame cómodo de exportar.
    dataframe = pd.DataFrame(construir_filas(resultado))

    # Escribe el DataFrame en formato Excel sin índice artificial.
    dataframe.to_excel(destino, index=False)

    # Devuelve la ruta del archivo generado.
    return destino


# Exporta un informe ejecutivo en Word.
def exportar_word(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un informe básico en formato Word.

    Parameters
    ----------
    resultado : ResultadoAuditoria
        Resultado de la auditoría.
    path_salida : Path
        Carpeta destino.

    Returns
    -------
    Path
        Ruta del archivo generado.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta de salida del documento Word.
    destino = path_salida / "informe_seo.docx"

    # Crea un nuevo documento Word vacío.
    documento = Document()

    # Añade el título principal del informe.
    documento.add_heading("Informe SEO profesional", level=1)

    # Añade un párrafo con el sitemap auditado.
    documento.add_paragraph(f"Sitemap auditado: {resultado.sitemap}")

    # Añade un párrafo con el número total de URLs analizadas.
    documento.add_paragraph(f"Total de URLs analizadas: {resultado.total_urls}")

    # Añade un bloque con el resumen de IA cuando exista.
    if resultado.resumen_ia:
        # Inserta un subtítulo para separar la parte narrativa.
        documento.add_heading("Resumen ejecutivo con IA", level=2)

        # Inserta el contenido narrativo generado por IA.
        documento.add_paragraph(resultado.resumen_ia)

    # Añade un subtítulo para el detalle de URLs.
    documento.add_heading("Detalle técnico", level=2)

    # Recorre cada URL para documentar su resultado en Word.
    for item in resultado.resultados:
        # Añade un subtítulo por URL analizada.
        documento.add_heading(item.url, level=3)

        # Añade el resumen técnico principal de la URL.
        documento.add_paragraph(
            f"Tipo: {item.tipo} | Estado HTTP: {item.estado_http} | Redirecciona: {item.redirecciona} | Noindex: {item.noindex}"
        )

        # Añade el title extraído.
        documento.add_paragraph(f"Title: {item.title}")

        # Añade el H1 extraído.
        documento.add_paragraph(f"H1: {item.h1}")

        # Añade la canonical extraída.
        documento.add_paragraph(f"Canonical: {item.canonical or ''}")

        # Recorre los hallazgos para listarlos en el documento.
        for hallazgo in item.hallazgos:
            # Añade una viñeta por cada hallazgo detectado.
            documento.add_paragraph(
                f"[{hallazgo.severidad.upper()}] {hallazgo.descripcion} -> {hallazgo.recomendacion}",
                style="List Bullet",
            )

    # Guarda el documento en la ruta final.
    documento.save(destino)

    # Devuelve la ruta del archivo generado.
    return destino


# Exporta un PDF simple con el resumen principal del informe.
def exportar_pdf(resultado: ResultadoAuditoria, path_salida: Path) -> Path:
    """
    Genera un PDF simple para entrega rápida.

    Parameters
    ----------
    resultado : ResultadoAuditoria
        Resultado de la auditoría.
    path_salida : Path
        Carpeta destino.

    Returns
    -------
    Path
        Ruta del archivo generado.
    """

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta final del PDF.
    destino = path_salida / "informe_seo.pdf"

    # Crea el lienzo PDF con tamaño A4.
    pdf = canvas.Canvas(str(destino), pagesize=A4)

    # Inicializa la posición vertical del cursor de escritura.
    posicion_y = 800

    # Escribe el título principal del documento.
    pdf.drawString(40, posicion_y, "Informe SEO profesional")

    # Desplaza el cursor hacia abajo para el siguiente contenido.
    posicion_y -= 20

    # Escribe el sitemap auditado.
    pdf.drawString(40, posicion_y, f"Sitemap: {resultado.sitemap}")

    # Desplaza el cursor para la siguiente línea.
    posicion_y -= 20

    # Escribe el total de URLs auditadas.
    pdf.drawString(40, posicion_y, f"Total URLs: {resultado.total_urls}")

    # Desplaza el cursor para empezar el bloque descriptivo.
    posicion_y -= 30

    # Obtiene el texto narrativo más útil para la portada del PDF.
    texto = resultado.resumen_ia or "No se ha generado resumen con IA en esta ejecución."

    # Recorre el texto por líneas para pintarlo de forma simple.
    for linea in texto.splitlines():
        # Evita escribir líneas vacías sin utilidad visual.
        if not linea.strip():
            # Mueve el cursor un poco para respetar el salto de línea.
            posicion_y -= 12

            # Continúa con la siguiente línea del texto.
            continue

        # Crea páginas nuevas si se acaba el espacio vertical.
        if posicion_y < 50:
            # Finaliza la página actual del PDF.
            pdf.showPage()

            # Reinicia el cursor vertical en la nueva página.
            posicion_y = 800

        # Escribe la línea actual en el PDF.
        pdf.drawString(40, posicion_y, linea[:110])

        # Desplaza el cursor para la siguiente línea.
        posicion_y -= 14

    # Guarda y cierra el archivo PDF.
    pdf.save()

    # Devuelve la ruta del archivo generado.
    return destino


# Exporta el informe IA en Markdown para edición y revisión humana.
def exportar_markdown_ia(resultado: ResultadoAuditoria, path_salida: Path) -> Path | None:
    """
    Genera un archivo Markdown con el resumen IA cuando exista.

    Parameters
    ----------
    resultado : ResultadoAuditoria
        Resultado global de la auditoría.
    path_salida : Path
        Carpeta destino.

    Returns
    -------
    Path | None
        Ruta del archivo generado o `None` si no hay resumen IA.
    """

    # Sale sin crear archivo cuando no existe resumen IA.
    if not resultado.resumen_ia:
        # Devuelve None para indicar ausencia de artefacto.
        return None

    # Garantiza la existencia de la carpeta de salida.
    asegurar_directorio(path_salida)

    # Define la ruta del archivo Markdown.
    destino = path_salida / "informe_ia.md"

    # Escribe el contenido del informe IA en UTF-8.
    destino.write_text(resultado.resumen_ia, encoding="utf-8")

    # Devuelve la ruta del archivo generado.
    return destino
