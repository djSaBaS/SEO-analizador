# Importa herramientas para construir dataframe de prueba.
import pandas as pd

# Importa helper de indexación a validar.
# Importa helpers de indexación a validar.
from seo_auditor.indexacion import _extraer_disallow_por_user_agent, generar_gestion_indexacion_inteligente

# Importa modelos para construir escenarios de auditoría.
from seo_auditor.models import HallazgoSeo, MetricaGscPagina, ResultadoUrl


# Verifica que Disallow se filtre correctamente por User-agent objetivo.
def test_extraer_disallow_por_user_agent_filtra_bloques() -> None:
    """Comprueba que solo se extraigan reglas Disallow del bloque aplicable."""

    # Construye dataframe simulando robots con dos bloques de agentes.
    robots_df = pd.DataFrame(
        [
            {"directive": "user-agent", "content": "Googlebot"},
            {"directive": "disallow", "content": "/privado-google/"},
            {"directive": "user-agent", "content": "*"},
            {"directive": "disallow", "content": "/privado-global/"},
        ]
    )

    # Extrae patrones para wildcard global.
    patrones = _extraer_disallow_por_user_agent(robots_df, "*")

    # Verifica que se conserve la regla global esperada.
    assert "/privado-global/" in patrones

    # Verifica que no se arrastre regla exclusiva de Googlebot.
    assert "/privado-google/" not in patrones


# Valida clasificación inteligente con señales URL, contenido, SEO y GSC.
def test_generar_gestion_indexacion_inteligente_clasifica_reglas_clave() -> None:
    """Comprueba clasificación INDEXABLE/REVISAR/NO_INDEXAR con motivos y prioridad."""

    # Crea URL transaccional con noindex para exclusión directa.
    url_no_indexar = ResultadoUrl(
        url="https://ejemplo.com/gracias?utm_source=mail",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/gracias",
        title="Gracias por completar el formulario",
        h1="Gracias",
        meta_description="Confirmación",
        canonical="https://ejemplo.com/gracias",
        noindex=True,
        hallazgos=[],
        palabras=40,
        texto_extraido="Gracias por enviar el formulario.",
    )

    # Crea URL indexable pero con señales de revisión y GSC sin clics.
    url_revisar = ResultadoUrl(
        url="https://ejemplo.com/blog/guia-seo",
        tipo="post",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/blog/guia-seo",
        title="Guía SEO",
        h1="",
        meta_description="",
        canonical="https://ejemplo.com/blog/guia-seo",
        noindex=False,
        hallazgos=[
            HallazgoSeo(
                tipo="arquitectura",
                severidad="media",
                descripcion="URL huérfana sin enlazado interno suficiente.",
                recomendacion="Añadir enlaces internos desde categorías.",
                area="Arquitectura",
                impacto="Medio",
                esfuerzo="Bajo",
                prioridad="P2",
            )
        ],
        palabras=100,
        texto_extraido="Contenido breve.",
    )

    # Crea URL sana para clasificación indexable.
    url_indexable = ResultadoUrl(
        url="https://ejemplo.com/servicios/seo-tecnico",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/servicios/seo-tecnico",
        title="Servicio SEO técnico",
        h1="SEO técnico",
        meta_description="Servicio completo",
        canonical="https://ejemplo.com/servicios/seo-tecnico",
        noindex=False,
        hallazgos=[],
        palabras=650,
        texto_extraido="Contenido extenso de valor.",
    )

    # Construye métricas GSC para reforzar reglas de revisión.
    metricas_gsc = [
        MetricaGscPagina(
            url="https://ejemplo.com/blog/guia-seo",
            clicks=0.0,
            impresiones=250.0,
            ctr=0.0,
            posicion_media=8.0,
        )
    ]

    # Ejecuta clasificación inteligente de indexación.
    decisiones = generar_gestion_indexacion_inteligente([url_no_indexar, url_revisar, url_indexable], metricas_gsc)

    # Construye índice rápido por URL para aserciones claras.
    indice = {item.url: item for item in decisiones}

    # Verifica que URL de confirmación quede en NO_INDEXAR.
    assert indice["https://ejemplo.com/gracias?utm_source=mail"].clasificacion == "NO_INDEXAR"

    # Verifica que URL con señales débiles y GSC quede en REVISAR.
    assert indice["https://ejemplo.com/blog/guia-seo"].clasificacion == "REVISAR"

    # Verifica que URL sana quede INDEXABLE.
    assert indice["https://ejemplo.com/servicios/seo-tecnico"].clasificacion == "INDEXABLE"


# Valida que los patrones se evalúen por segmento y no por subcadenas.
def test_generar_gestion_indexacion_no_marca_formacion_como_form() -> None:
    """Comprueba que /formacion no se clasifique como NO_INDEXAR por coincidencia parcial."""

    # Crea URL con segmento /formacion que no debe disparar /form.
    url_formacion = ResultadoUrl(
        url="https://ejemplo.com/formacion-seo",
        tipo="page",
        estado_http=200,
        redirecciona=False,
        url_final="https://ejemplo.com/formacion-seo",
        title="Formación SEO",
        h1="Formación SEO",
        meta_description="Curso",
        canonical="https://ejemplo.com/formacion-seo",
        noindex=False,
        hallazgos=[],
        palabras=700,
        texto_extraido="Contenido amplio para formación.",
    )

    # Ejecuta clasificación sobre la URL de prueba.
    decision = generar_gestion_indexacion_inteligente([url_formacion])[0]

    # Verifica que la URL no se marque como no indexable por falso positivo.
    assert decision.clasificacion == "INDEXABLE"


# Valida cruce GSC con normalización de URL auditada/final.
def test_generar_gestion_indexacion_aplica_gsc_con_url_normalizada() -> None:
    """Comprueba lookup GSC con diferencias de slash final o URL final."""

    # Crea URL auditada sin slash final y URL final con slash.
    url_auditada = ResultadoUrl(
        url="https://ejemplo.com/about",
        tipo="page",
        estado_http=200,
        redirecciona=True,
        url_final="https://ejemplo.com/about/",
        title="About",
        h1="About",
        meta_description="Acerca",
        canonical="https://ejemplo.com/about/",
        noindex=False,
        hallazgos=[],
        palabras=500,
        texto_extraido="Contenido correcto.",
    )

    # Define métrica GSC solo con variante de slash final.
    metricas_gsc = [
        MetricaGscPagina(
            url="https://ejemplo.com/about/",
            clicks=0.0,
            impresiones=120.0,
            ctr=0.0,
            posicion_media=12.0,
        )
    ]

    # Ejecuta clasificación con señales GSC.
    decision = generar_gestion_indexacion_inteligente([url_auditada], metricas_gsc)[0]

    # Verifica que la señal GSC se aplique y fuerce revisión.
    assert decision.clasificacion == "REVISAR"
