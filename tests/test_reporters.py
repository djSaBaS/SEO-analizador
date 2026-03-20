# Importa modelos del dominio para fabricar una auditoría mínima de prueba.
from seo_auditor.models import HallazgoSeo, ResultadoAuditoria, ResultadoUrl

# Importa funciones de reporters bajo prueba.
from seo_auditor.reporters import calcular_metricas, construir_secciones_desde_ia, sanear_texto_para_pdf


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
