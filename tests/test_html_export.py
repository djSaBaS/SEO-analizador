# Importa Path para manejar archivos temporales.
from pathlib import Path

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
