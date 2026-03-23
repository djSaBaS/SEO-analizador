# Importa los modelos del dominio para construir datos de prueba.
from seo_auditor.models import HallazgoSeo, ResultadoAuditoria, ResultadoUrl

# Importa funciones a validar del analizador.
from seo_auditor.analyzer import _clasificar_canonical, _es_redireccion_solo_slash, _normalizar_url_comparable, clasificar_hallazgo

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


# Verifica que la normalización de slash se detecte como redirección trivial.
def test_es_redireccion_solo_slash_detecta_normalizacion() -> None:
    """Comprueba que la comparación de slash final detecte cambios triviales."""

    # Evalúa origen sin slash y destino con slash.
    resultado = _es_redireccion_solo_slash("https://ejemplo.com/pagina", "https://ejemplo.com/pagina/")

    # Verifica detección correcta de redirección trivial.
    assert resultado is True


# Verifica que la normalización de URL elimine diferencias irrelevantes.
def test_normalizar_url_comparable_equivalencia_basica() -> None:
    """Comprueba que esquema/host/puerto/fragmento se normalicen para comparar canonical."""

    # Normaliza URL con mayúsculas, puerto por defecto y fragmento.
    normalizada = _normalizar_url_comparable("HTTPS://EJEMPLO.COM:443/ruta/?b=2&a=1#seccion")

    # Verifica resultado normalizado esperado.
    assert normalizada == "https://ejemplo.com/ruta?a=1&b=2"


# Verifica que diferencias de slash final no escalen como incoherencia real.
def test_clasificar_canonical_diferencia_menor_por_slash() -> None:
    """Comprueba que una diferencia menor de slash final se clasifique como menor."""

    # Evalúa canonical equivalente con slash final en URL 200.
    estado = _clasificar_canonical("https://ejemplo.com/pagina", "https://ejemplo.com/pagina", "https://ejemplo.com/pagina/", 200)

    # Verifica clasificación de baja severidad.
    assert estado == "coherente"


# Verifica que una canonical idéntica se considere coherente.
def test_clasificar_canonical_coherente_no_genera_desviacion() -> None:
    """Comprueba que una canonical igual a la URL final no se clasifique como incidencia."""

    # Evalúa canonical autorreferente exacta.
    estado = _clasificar_canonical("https://ejemplo.com/pagina", "https://ejemplo.com/pagina", "https://ejemplo.com/pagina", 200)

    # Verifica clasificación coherente.
    assert estado == "coherente"


# Verifica que cambios de URL relevantes sí se clasifiquen como incoherencia real.
def test_clasificar_canonical_incoherente_real() -> None:
    """Comprueba que una canonical en ruta distinta se marque como incoherente."""

    # Evalúa canonical en ruta diferente y no equivalente.
    estado = _clasificar_canonical("https://ejemplo.com/a", "https://ejemplo.com/a", "https://ejemplo.com/otra-url", 200)

    # Verifica clasificación de incoherencia real.
    assert estado == "incoherente"


# Verifica que puertos inválidos en canonical no rompan toda la auditoría.
def test_normalizar_url_comparable_tolera_puerto_invalido() -> None:
    """Comprueba que la normalización no lanza excepción ante puertos malformados."""

    # Normaliza URL con puerto inválido para asegurar tolerancia.
    normalizada = _normalizar_url_comparable("https://ejemplo.com:abc/ruta")

    # Verifica que se conserve una URL comparable utilizable.
    assert normalizada == "https://ejemplo.com/ruta"
