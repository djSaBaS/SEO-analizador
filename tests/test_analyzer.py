# Importa los modelos del dominio para construir datos de prueba.
from seo_auditor.models import HallazgoSeo, ResultadoAuditoria, ResultadoUrl

# Importa el exportador tabular para validar la salida.
from seo_auditor.reporters import construir_filas


# Verifica que la exportación tabular conserve campos clave.
def test_construir_filas_generar_campos_esperados() -> None:
    """Comprueba que la fila tabular incluya la información relevante del resultado."""

    # Crea un hallazgo de prueba representativo.
    hallazgo = HallazgoSeo(
        tipo="indexación",
        severidad="alta",
        descripcion="La URL redirecciona.",
        recomendacion="Actualizar enlaces internos.",
    )

    # Crea un resultado de URL de prueba con un hallazgo.
    resultado_url = ResultadoUrl(
        url="https://www.ejemplo.com/origen",
        tipo="page",
        estado_http=301,
        redirecciona=True,
        url_final="https://www.ejemplo.com/destino",
        title="Página de ejemplo",
        h1="Título ejemplo",
        meta_description="Descripción de ejemplo",
        canonical="https://www.ejemplo.com/destino",
        noindex=False,
        hallazgos=[hallazgo],
    )

    # Crea el resultado global de auditoría con una sola URL.
    auditoria = ResultadoAuditoria(
        sitemap="https://www.ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[resultado_url],
    )

    # Convierte la auditoría en filas tabulares.
    filas = construir_filas(auditoria)

    # Recupera la única fila generada para validarla.
    fila = filas[0]

    # Verifica que la URL original se conserve.
    assert fila["url"] == "https://www.ejemplo.com/origen", "La URL exportada no coincide con la esperada."

    # Verifica que el estado HTTP se conserve.
    assert fila["estado_http"] == 301, "El estado HTTP exportado no coincide con el esperado."

    # Verifica que la recomendación aparezca en la fila resumida.
    assert "Actualizar enlaces internos." in fila["recomendaciones"], "La recomendación no se exportó correctamente."
