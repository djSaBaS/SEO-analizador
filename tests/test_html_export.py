# Importa Path para manejar archivos temporales.
from pathlib import Path
import re

# Importa modelos de dominio para construir auditoría sintética.
from seo_auditor.models import DatosAnalytics, HallazgoSeo, ResultadoAuditoria, ResultadoUrl

# Importa exportador HTML bajo prueba.
from seo_auditor.reporters import exportar_html


# Verifica que el HTML ordene incidencias por severidad descendente.
def test_exportar_html_orden_severidad(tmp_path: Path) -> None:
    """Comprueba que incidencias altas aparezcan antes que informativas en el detalle HTML."""

    # Crea hallazgo de severidad informativa.
    hallazgo_info = HallazgoSeo(
        tipo="contenido",
        severidad="informativa",
        descripcion="Detalle menor informativo",
        recomendacion="Monitorizar",
        area="Contenido",
        impacto="Bajo",
        esfuerzo="Bajo",
        prioridad="P4",
    )

    # Crea hallazgo de severidad alta.
    hallazgo_alto = HallazgoSeo(
        tipo="indexación",
        severidad="alta",
        descripcion="Incidencia crítica de indexación",
        recomendacion="Corregir rápido",
        area="Indexación",
        impacto="Alto",
        esfuerzo="Bajo",
        prioridad="P1",
    )

    # Construye URL con hallazgo informativo.
    url_info = ResultadoUrl(
        url="https://ejemplo.com/info",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/info",
        title="Info",
        h1="Info",
        meta_description="Info",
        canonical="https://ejemplo.com/info",
        noindex=False,
        hallazgos=[hallazgo_info],
    )

    # Construye URL con hallazgo alto.
    url_alta = ResultadoUrl(
        url="https://ejemplo.com/alta",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/alta",
        title="Alta",
        h1="Alta",
        meta_description="Alta",
        canonical="https://ejemplo.com/alta",
        noindex=False,
        hallazgos=[hallazgo_alto],
    )

    # Construye auditoría de prueba con ambas URLs.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=2,
        resultados=[url_info, url_alta],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-23",
        gestor="Gestor",
        periodo_date_from="2026-02-23",
        periodo_date_to="2026-03-22",
    )

    # Exporta HTML a carpeta temporal.
    ruta_html = exportar_html(auditoria, tmp_path)

    # Lee contenido HTML para validación de orden.
    contenido = ruta_html.read_text(encoding="utf-8")

    # Localiza la posición de cada URL en la tabla de detalle.
    indice_alta = contenido.find("https://ejemplo.com/alta")

    # Localiza URL informativa en contenido generado.
    indice_info = contenido.find("https://ejemplo.com/info")

    # Verifica que la URL alta aparezca antes que la informativa.
    assert indice_alta != -1 and indice_info != -1 and indice_alta < indice_info

    # Verifica que la cabecera incluya periodo analizado visible.
    assert "Periodo analizado" in contenido and "2026-02-23 - 2026-03-22" in contenido


# Verifica que el colspan vacío sea dinámico según columnas de la tabla.
def test_exportar_html_colspan_dinamico_en_tablas_vacias(tmp_path: Path) -> None:
    """Comprueba que tablas vacías usen colspan acorde al número de columnas."""

    # Construye auditoría sin datos de Analytics para forzar tabla vacía de comportamiento.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-26",
        gestor="Gestor",
        analytics=DatosAnalytics(activo=True, paginas=[]),
    )

    # Exporta HTML para validar contenido.
    ruta_html = exportar_html(auditoria, tmp_path)

    # Lee contenido generado.
    contenido = ruta_html.read_text(encoding="utf-8")

    # Verifica que exista colspan esperado de 6 columnas para comportamiento.
    assert 'colspan="6">No disponible' in contenido


# Verifica que el HTML final no exponga placeholders técnicos entre corchetes.
def test_exportar_html_no_expone_tokens_placeholder_mayusculas(tmp_path: Path) -> None:
    """Comprueba ausencia de patrones [A-Z_] en el HTML exportable final."""

    # Crea hallazgo con placeholders para validar sanitización final.
    hallazgo = HallazgoSeo(
        tipo="contenido",
        severidad="alta",
        descripcion="Corregir [ALTA_PRIORIDAD] en snippets.",
        recomendacion="Aplicar [OBJETIVO_Q2] y revisar titles.",
        area="Contenido",
        impacto="Alto",
        esfuerzo="Bajo",
        prioridad="P1",
    )

    # Construye URL de prueba con el hallazgo placeholder.
    url = ResultadoUrl(
        url="https://ejemplo.com/test",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/test",
        title="Landing [OBJETIVO]",
        h1="H1 [ALTA_PRIORIDAD]",
        meta_description="Meta de prueba",
        canonical="https://ejemplo.com/test",
        noindex=False,
        hallazgos=[hallazgo],
    )

    # Construye auditoría mínima para exportar HTML.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[url],
        cliente="Cliente [OBJETIVO]",
        fecha_ejecucion="2026-03-29",
        gestor="Gestor [ALTA_PRIORIDAD]",
    )

    # Exporta HTML y lee contenido final para validación.
    contenido = exportar_html(auditoria, tmp_path).read_text(encoding="utf-8")

    # Verifica que no queden placeholders en mayúsculas entre corchetes.
    assert re.search(r"\[[A-Z_]+\]", contenido) is None


# Verifica cabecera ejecutiva de metadatos con periodo destacado.
def test_exportar_html_incluye_meta_ejecutiva_y_periodo_destacado(tmp_path: Path) -> None:
    """Comprueba presencia del bloque meta superior con periodo visible."""

    # Construye auditoría con periodo explícito.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[],
        cliente="Cliente HTML",
        fecha_ejecucion="2026-03-29",
        gestor="Gestor HTML",
        periodo_date_from="2026-03-01",
        periodo_date_to="2026-03-28",
    )

    # Exporta HTML y lee contenido de salida.
    contenido = exportar_html(auditoria, tmp_path).read_text(encoding="utf-8")

    # Valida presencia de bloque ejecutivo y periodo destacado.
    assert "meta-ejecutiva" in contenido
    assert "periodo-destacado" in contenido
    assert "Periodo desde:</b> 2026-03-01" in contenido
    assert "Periodo hasta:</b> 2026-03-28" in contenido


# Verifica fallback de periodo en HTML cuando no hay fechas.
def test_exportar_html_periodo_fallback_sin_fechas(tmp_path: Path) -> None:
    """Comprueba etiqueta No disponible cuando faltan fechas de periodo."""

    # Crea auditoría sin rango de fechas.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[],
        cliente="Cliente HTML",
        fecha_ejecucion="2026-03-29",
        gestor="Gestor HTML",
    )

    # Exporta contenido HTML para validación.
    contenido = exportar_html(auditoria, tmp_path).read_text(encoding="utf-8")

    # Verifica fallback visible en cabecera ejecutiva.
    assert "Periodo analizado: No disponible" in contenido


# Valida estructura premium de contenedores HTML y secciones obligatorias.
def test_exportar_html_estructura_contenedores_clave(tmp_path: Path) -> None:
    """Comprueba que el HTML exportado incluya bloques semánticos obligatorios."""

    # Construye auditoría mínima con un hallazgo para poblar tabla técnica.
    hallazgo = HallazgoSeo(
        tipo="rendimiento",
        severidad="media",
        descripcion="LCP por encima de objetivo.",
        recomendacion="Optimizar recursos críticos.",
        area="Rendimiento",
        impacto="Medio",
        esfuerzo="Medio",
        prioridad="P2",
    )

    # Crea resultado de URL mínimo para activar detalle técnico.
    resultado_url = ResultadoUrl(
        url="https://ejemplo.com/",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/",
        title="Inicio",
        h1="Inicio",
        meta_description="Descripción",
        canonical="https://ejemplo.com/",
        noindex=False,
        hallazgos=[hallazgo],
    )

    # Crea auditoría con metadatos editoriales completos.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[resultado_url],
        cliente="Cliente Estructura",
        fecha_ejecucion="2026-03-29",
        gestor="Gestor Estructura",
        periodo_date_from="2026-03-01",
        periodo_date_to="2026-03-28",
    )

    # Exporta y carga contenido HTML resultante.
    contenido = exportar_html(auditoria, tmp_path).read_text(encoding="utf-8")

    # Comprueba contenedores semánticos principales del layout premium.
    assert 'class="cabecera"' in contenido
    assert 'class="meta"' in contenido
    assert "kpi-card" in contenido
    assert "prioridad" in contenido
    assert "tabla-ejecutiva" in contenido

    # Verifica secciones editoriales obligatorias.
    assert "KPIs ejecutivos" in contenido
    assert "Prioridades y quick wins" in contenido
    assert "Incidencias técnicas (detalle)" in contenido
