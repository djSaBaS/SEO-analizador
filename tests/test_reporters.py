# Importa Path para construir rutas temporales de prueba.
from pathlib import Path

# Importa modelos del dominio para fabricar una auditoría mínima de prueba.
from seo_auditor.models import HallazgoSeo, OportunidadRendimiento, ResultadoAuditoria, ResultadoRendimiento, ResultadoUrl

# Importa funciones de reporters bajo prueba.
from seo_auditor.reporters import _construir_bloques_narrativos, calcular_metricas, construir_secciones_desde_ia, exportar_excel, sanear_texto_para_pdf

# Importa lector de libros Excel para validar KPIs.
from openpyxl import load_workbook


# Verifica que el saneamiento escape etiquetas potencialmente problemáticas.
def test_sanear_texto_para_pdf_escapa_marcado_html() -> None:
    """Comprueba que el texto con etiquetas HTML se escape para reportlab."""

    # Define un texto con etiquetas que pueden romper el parser de reportlab.
    texto = "Etiqueta <link rel='canonical' href='https://ejemplo.com'> y <b>negrita</b>."

    # Ejecuta el saneamiento antes de generar el PDF.
    saneado = sanear_texto_para_pdf(texto)

    # Verifica que la etiqueta se haya escapado correctamente.
    assert "&lt;link rel='canonical' href='https://ejemplo.com'&gt;" in saneado

    # Verifica que también se haya escapado el cierre de negrita.
    assert "&lt;b&gt;negrita&lt;/b&gt;" in saneado


# Verifica que la transformación de markdown IA cree secciones limpias.
def test_construir_secciones_desde_ia_limpia_markdown() -> None:
    """Comprueba conversión de markdown crudo a estructura de secciones."""

    # Define texto IA con markdown mixto.
    texto = "## Resumen ejecutivo\n**Texto clave**\n- Punto uno\n- Punto dos\n---\n### Roadmap\n1. Acción A"

    # Convierte texto en estructura intermedia.
    secciones = construir_secciones_desde_ia(texto)

    # Verifica que existan secciones con contenido.
    assert len(secciones) >= 2

    # Verifica que no persista markdown crudo en items.
    assert "**" not in " ".join(str(item) for seccion in secciones for item in seccion["items"])


# Verifica que el score SEO no sea excesivamente punitivo por defecto.
def test_calcular_metricas_score_ponderado() -> None:
    """Comprueba que la fórmula de score devuelva un valor razonable."""

    # Crea un hallazgo de severidad alta para la muestra.
    hallazgo = HallazgoSeo(
        tipo="indexación",
        severidad="alta",
        descripcion="La URL redirecciona.",
        recomendacion="Actualizar URL final.",
        area="Arquitectura",
        impacto="Alto",
        esfuerzo="Bajo",
        prioridad="P1",
    )

    # Construye un resultado URL con una incidencia.
    resultado_url = ResultadoUrl(
        url="https://ejemplo.com/a",
        tipo="page",
        estado_http=301,
        redirecciona=True,
        url_final="https://ejemplo.com/b",
        title="Página",
        h1="H1",
        meta_description="Meta",
        canonical="https://ejemplo.com/b",
        noindex=False,
        hallazgos=[hallazgo],
    )

    # Construye una auditoría mínima de ejemplo.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[resultado_url],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-19",
        gestor="Juan Antonio Sánchez Plaza",
    )

    # Calcula métricas agregadas.
    metricas = calcular_metricas(auditoria)

    # Verifica que el score esté en el rango operativo esperado.
    assert 5.0 <= float(metricas["score"]) <= 100.0


# Verifica que se rellenen secciones obligatorias cuando no haya IA.
def test_construir_bloques_narrativos_generar_fallback_completo() -> None:
    """Comprueba que todas las secciones narrativas tengan contenido de fallback."""

    # Crea un hallazgo representativo para alimentar secciones.
    hallazgo = HallazgoSeo(
        tipo="contenido",
        severidad="alta",
        descripcion="Falta title.",
        recomendacion="Definir title único.",
        area="Contenido",
        impacto="Alto",
        esfuerzo="Bajo",
        prioridad="P1",
    )

    # Construye un resultado URL mínimo.
    resultado_url = ResultadoUrl(
        url="https://ejemplo.com/a",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/a",
        title="",
        h1="H1",
        meta_description="Meta",
        canonical="https://ejemplo.com/a",
        noindex=False,
        hallazgos=[hallazgo],
    )

    # Construye una auditoría sin resumen IA para forzar fallback.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[resultado_url],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-20",
        gestor="Gestor",
    )

    # Genera bloques narrativos por fallback.
    bloques = _construir_bloques_narrativos(auditoria)

    # Verifica que cada sección obligatoria tenga al menos una línea.
    assert all(len(items) > 0 for items in bloques.values())


# Verifica que la media de score de dashboard use ejecuciones únicas.
def test_exportar_excel_score_medio_desde_ejecuciones_unicas(tmp_path: Path) -> None:
    """Comprueba que KPI de score medio no se sesgue por número de oportunidades."""

    # Crea resultado URL mínimo para construir auditoría válida.
    resultado_url = ResultadoUrl(
        url="https://ejemplo.com",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com",
        title="Home",
        h1="Inicio",
        meta_description="Meta",
        canonical="https://ejemplo.com",
        noindex=False,
        hallazgos=[],
    )

    # Crea oportunidades duplicadas en un mismo análisis móvil.
    oportunidades = [
        OportunidadRendimiento(id_oportunidad="op1", titulo="Reducir JS", descripcion="...", ahorro_estimado="500 ms", severidad="alta"),
        OportunidadRendimiento(id_oportunidad="op2", titulo="Optimizar imágenes", descripcion="...", ahorro_estimado="300 ms", severidad="media"),
    ]

    # Construye resultados de rendimiento por estrategia.
    rendimiento = [
        ResultadoRendimiento(
            url="https://ejemplo.com",
            estrategia="mobile",
            performance_score=50.0,
            accessibility_score=90.0,
            best_practices_score=90.0,
            seo_score=90.0,
            lcp="2,5 s",
            cls="0,10",
            inp="200 ms",
            fcp="1,2 s",
            tbt="100 ms",
            speed_index="2,0 s",
            campo_lcp=None,
            campo_cls=None,
            campo_inp=None,
            oportunidades=oportunidades,
        ),
        ResultadoRendimiento(
            url="https://ejemplo.com",
            estrategia="mobile",
            performance_score=100.0,
            accessibility_score=95.0,
            best_practices_score=95.0,
            seo_score=95.0,
            lcp="1,0 s",
            cls="0,01",
            inp="100 ms",
            fcp="0,8 s",
            tbt="0 ms",
            speed_index="1,0 s",
            campo_lcp=None,
            campo_cls=None,
            campo_inp=None,
            oportunidades=[],
        ),
    ]

    # Construye auditoría con rendimiento para exportación.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[resultado_url],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-20",
        gestor="Gestor",
        rendimiento=rendimiento,
    )

    # Exporta el Excel de prueba en carpeta temporal.
    ruta_excel = exportar_excel(auditoria, tmp_path)

    # Abre libro generado para validación de KPI.
    libro = load_workbook(ruta_excel)

    # Obtiene hoja Dashboard.
    hoja_dashboard = libro["Dashboard"]

    # Verifica score medio móvil basado en ejecuciones únicas: (50 + 100) / 2 = 75.
    assert hoja_dashboard["B12"].value == 75.0


# Verifica que el dashboard conserve los gráficos esperados.
def test_exportar_excel_dashboard_contiene_graficos(tmp_path: Path) -> None:
    """Comprueba que el Dashboard exportado tenga gráficos visibles y cargados."""

    # Construye auditoría mínima para exportar Excel.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[
            ResultadoUrl(
                url="https://ejemplo.com",
                tipo="page",
                estado_http=200,
                redirecciona=False,
                url_final="https://ejemplo.com",
                title="Home",
                h1="Inicio",
                meta_description="Meta",
                canonical="https://ejemplo.com",
                noindex=False,
                hallazgos=[],
            )
        ],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-20",
        gestor="Gestor",
    )

    # Exporta libro para inspeccionar gráficos.
    ruta_excel = exportar_excel(auditoria, tmp_path)

    # Carga libro recién exportado.
    libro = load_workbook(ruta_excel)

    # Obtiene hoja dashboard para validar gráficos.
    dashboard = libro["Dashboard"]

    # Verifica que existan al menos tres gráficos.
    assert len(dashboard._charts) >= 3


# Verifica que la hoja de errores mantenga color por severidad.
def test_exportar_excel_aplica_color_por_severidad(tmp_path: Path) -> None:
    """Comprueba que la fila de error reciba un color suave según severidad."""

    # Crea hallazgo de severidad crítica para validar color.
    hallazgo = HallazgoSeo(
        tipo="indexación",
        severidad="crítica",
        descripcion="Error 5xx.",
        recomendacion="Corregir servidor.",
        area="Infraestructura",
        impacto="Muy alto",
        esfuerzo="Medio",
        prioridad="P1",
    )

    # Construye resultado URL con incidencia crítica.
    resultado_url = ResultadoUrl(
        url="https://ejemplo.com",
        tipo="page",
        estado_http=500,
        redirecciona=False,
        url_final="https://ejemplo.com",
        title="Home",
        h1="Inicio",
        meta_description="Meta",
        canonical="https://ejemplo.com",
        noindex=False,
        hallazgos=[hallazgo],
    )

    # Construye auditoría para exportación.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[resultado_url],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-20",
        gestor="Gestor",
    )

    # Exporta Excel con datos críticos.
    ruta_excel = exportar_excel(auditoria, tmp_path)

    # Carga libro exportado.
    libro = load_workbook(ruta_excel)

    # Obtiene hoja de errores.
    errores = libro["Errores"]

    # Obtiene color de fondo de la primera fila de datos.
    color = errores["A2"].fill.fgColor.rgb or ""

    # Verifica que se haya aplicado un color distinto a blanco.
    assert "FDECEA" in color


# Verifica que la sección de rendimiento no use valores None como datos reales.
def test_construir_bloques_narrativos_rendimiento_fallido_muestra_mensaje_profesional() -> None:
    """Comprueba que, ante fallo de PageSpeed, se renderice mensaje profesional y no valores vacíos."""

    # Construye auditoría mínima con estado fallido de PageSpeed.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-20",
        gestor="Gestor",
        fuentes_fallidas=["pagespeed"],
        pagespeed_estado={"https://ejemplo.com/": {"mobile": "timeout"}},
    )

    # Genera bloques narrativos.
    bloques = _construir_bloques_narrativos(auditoria)

    # Consolida sección de rendimiento.
    texto = " ".join(bloques["Rendimiento y experiencia de usuario"])

    # Verifica mensaje profesional de indisponibilidad.
    assert "No se pudieron obtener métricas de PageSpeed" in texto


# Verifica que la tabla de rendimiento se cree con rango válido.
def test_exportar_excel_tabla_rendimiento_valida(tmp_path: Path) -> None:
    """Comprueba que la tabla de rendimiento exista y tenga rango consistente."""

    # Construye auditoría con una fila de rendimiento para crear tabla.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-20",
        gestor="Gestor",
        rendimiento=[
            ResultadoRendimiento(
                url="https://ejemplo.com",
                estrategia="mobile",
                performance_score=80.0,
                accessibility_score=90.0,
                best_practices_score=90.0,
                seo_score=95.0,
                lcp="2,0 s",
                cls="0,05",
                inp="200 ms",
                fcp="1,0 s",
                tbt="80 ms",
                speed_index="1,5 s",
                campo_lcp=None,
                campo_cls=None,
                campo_inp=None,
            )
        ],
    )

    # Exporta Excel para inspección de tabla.
    ruta_excel = exportar_excel(auditoria, tmp_path)

    # Carga libro generado.
    libro = load_workbook(ruta_excel)

    # Obtiene hoja de rendimiento.
    rendimiento = libro["Rendimiento"]

    # Verifica existencia de tabla y rango válido esperado.
    assert "TablaRendimiento" in rendimiento.tables
    assert rendimiento.tables["TablaRendimiento"].ref == "A1:T2"
