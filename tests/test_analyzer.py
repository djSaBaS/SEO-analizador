# Importa los modelos del dominio para construir datos de prueba.
from seo_auditor.models import HallazgoSeo, ResultadoAuditoria, ResultadoUrl

# Importa funciones a validar del analizador.
from seo_auditor.analyzer import clasificar_hallazgo

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
        area="Arquitectura",
        impacto="Alto",
        esfuerzo="Bajo",
        prioridad="P1",
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
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-19",
        gestor="Juan Antonio Sánchez Plaza",
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
    assert fila["recomendacion"] == "Actualizar enlaces internos.", "La recomendación no se exportó correctamente."


# Verifica que la clasificación automática respete reglas críticas.
def test_clasificar_hallazgo_detecta_5xx_como_critica() -> None:
    """Comprueba que los errores 5xx se clasifiquen con severidad crítica."""

    # Clasifica una descripción representativa de error de servidor.
    clasificacion = clasificar_hallazgo("técnico", "La URL devuelve un error 5xx y no es accesible para rastreo.")

    # Verifica que el nivel de severidad sea crítica.
    assert clasificacion["severidad"] == "crítica", "Un error 5xx debe ser clasificado como crítica."
