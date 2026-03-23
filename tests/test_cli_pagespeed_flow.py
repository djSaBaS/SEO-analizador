# Importa utilidades de tipos para construir argumentos simulados.
from types import SimpleNamespace

# Importa estructuras del dominio para fabricar resultados de prueba.
from seo_auditor.models import ResultadoAuditoria, ResultadoRendimiento, ResultadoUrl

# Importa módulo CLI bajo prueba.
from seo_auditor import cli

# Importa configuración tipada del proyecto.
from seo_auditor.config import Configuracion


# Verifica que PageSpeed persista datos y fuente activa en el flujo principal.
def test_main_persiste_rendimiento_y_fuente_pagespeed(monkeypatch, tmp_path) -> None:
    """Comprueba que el flujo CLI propague `rendimiento` y `pagespeed` al resultado final."""

    # Construye argumentos simulados de ejecución.
    argumentos = SimpleNamespace(
        sitemap="https://ejemplo.com/sitemap.xml",
        output=str(tmp_path),
        usar_ia=False,
        testia=False,
        modelo_ia="",
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        gestor="Gestor",
        max_muestras_ia=5,
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
    )

    # Define parser simulado para evitar CLI real.
    class _ParserFalso:
        """Parser mínimo que devuelve argumentos simulados."""

        # Devuelve argumentos preconstruidos.
        def parse_args(self):
            """Retorna argumentos simulados de forma estable."""
            return argumentos

    # Crea un resultado técnico base para el flujo.
    resultado_base = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[
            ResultadoUrl(
                url="https://ejemplo.com/",
                tipo="page",
                estado_http=200,
                redirecciona=False,
                url_final="https://ejemplo.com/",
                title="Inicio",
                h1="Inicio",
                meta_description="Meta",
                canonical="https://ejemplo.com/",
                noindex=False,
                hallazgos=[],
            )
        ],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-20",
        gestor="Gestor",
    )

    # Define resultado de PageSpeed simulado.
    resultado_rendimiento = ResultadoRendimiento(
        url="https://ejemplo.com/",
        estrategia="mobile",
        performance_score=88.0,
        accessibility_score=90.0,
        best_practices_score=92.0,
        seo_score=95.0,
        lcp="1,8 s",
        cls="0,02",
        inp="180 ms",
        fcp="1,1 s",
        tbt="90 ms",
        speed_index="1,5 s",
        campo_lcp=None,
        campo_cls=None,
        campo_inp=None,
    )

    # Inicializa capturador del resultado exportado.
    capturado = {}

    # Inyecta parser falso en el módulo CLI.
    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())

    # Inyecta configuración con clave de PageSpeed activa.
    monkeypatch.setattr(
        cli,
        "cargar_configuracion",
        lambda: Configuracion(
            gemini_api_key="",
            gemini_model="gemini-2.0-flash",
            pagespeed_api_key="clave-pagespeed",
            http_timeout=10,
            max_urls=10,
            max_pagepsi_urls=5,
            pagespeed_timeout=45,
            pagespeed_reintentos=2,
            cache_ttl_segundos=21600,
        ),
    )

    # Simula extracción de URLs desde sitemap.
    monkeypatch.setattr(cli, "extraer_urls_sitemap", lambda *args, **kwargs: ["https://ejemplo.com/"])

    # Simula auditoría técnica devolviendo el resultado base.
    monkeypatch.setattr(cli, "auditar_urls", lambda *args, **kwargs: resultado_base)

    # Simula ejecución de PageSpeed con un resultado válido.
    monkeypatch.setattr(cli, "_ejecutar_pagespeed", lambda *args, **kwargs: [resultado_rendimiento])

    # Captura el resultado que llega al exportador JSON.
    def _capturar_json(resultado, _path):
        """Guarda el resultado para validar persistencia de datos."""
        capturado["resultado"] = resultado
        return _path

    # Inyecta exportador JSON espía.
    monkeypatch.setattr(cli, "exportar_json", _capturar_json)

    # Inyecta exportadores restantes como no-op.
    monkeypatch.setattr(cli, "exportar_excel", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "exportar_word", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "exportar_pdf", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "exportar_markdown_ia", lambda *args, **kwargs: None)

    # Ejecuta flujo principal.
    codigo = cli.main()

    # Verifica ejecución correcta.
    assert codigo == 0

    # Verifica que existan resultados de rendimiento persistidos.
    assert capturado["resultado"].rendimiento

    # Verifica que se marque PageSpeed como fuente activa.
    assert "pagespeed" in capturado["resultado"].fuentes_activas


# Verifica que PageSpeed fallido no quede como fuente activa.
def test_main_no_marca_pagespeed_como_activa_si_falla(monkeypatch, tmp_path) -> None:
    """Comprueba que errores de PageSpeed se registren como fuente fallida."""

    # Construye argumentos simulados de ejecución.
    argumentos = SimpleNamespace(
        sitemap="https://ejemplo.com/sitemap.xml",
        output=str(tmp_path),
        usar_ia=False,
        testia=False,
        modelo_ia="",
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        gestor="Gestor",
        max_muestras_ia=5,
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
    )

    # Define parser simulado para evitar CLI real.
    class _ParserFalso:
        """Parser mínimo que devuelve argumentos simulados."""

        # Devuelve argumentos preconstruidos.
        def parse_args(self):
            """Retorna argumentos simulados de forma estable."""
            return argumentos

    # Crea un resultado técnico base para el flujo.
    resultado_base = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[
            ResultadoUrl(
                url="https://ejemplo.com/",
                tipo="page",
                estado_http=200,
                redirecciona=False,
                url_final="https://ejemplo.com/",
                title="Inicio",
                h1="Inicio",
                meta_description="Meta",
                canonical="https://ejemplo.com/",
                noindex=False,
                hallazgos=[],
            )
        ],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-20",
        gestor="Gestor",
    )

    # Define resultado de PageSpeed fallido.
    resultado_rendimiento = ResultadoRendimiento(
        url="https://ejemplo.com/",
        estrategia="mobile",
        performance_score=None,
        accessibility_score=None,
        best_practices_score=None,
        seo_score=None,
        lcp=None,
        cls=None,
        inp=None,
        fcp=None,
        tbt=None,
        speed_index=None,
        campo_lcp=None,
        campo_cls=None,
        campo_inp=None,
        error="timeout",
    )

    # Inicializa capturador del resultado exportado.
    capturado = {}

    # Inyecta parser falso en el módulo CLI.
    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())

    # Inyecta configuración con clave de PageSpeed activa.
    monkeypatch.setattr(
        cli,
        "cargar_configuracion",
        lambda: Configuracion(
            gemini_api_key="",
            gemini_model="gemini-2.0-flash",
            pagespeed_api_key="clave-pagespeed",
            http_timeout=10,
            max_urls=10,
            max_pagepsi_urls=5,
            pagespeed_timeout=45,
            pagespeed_reintentos=2,
            cache_ttl_segundos=21600,
        ),
    )

    # Simula extracción de URLs desde sitemap.
    monkeypatch.setattr(cli, "extraer_urls_sitemap", lambda *args, **kwargs: ["https://ejemplo.com/"])

    # Simula auditoría técnica devolviendo el resultado base.
    monkeypatch.setattr(cli, "auditar_urls", lambda *args, **kwargs: resultado_base)

    # Simula ejecución fallida de PageSpeed.
    monkeypatch.setattr(cli, "_ejecutar_pagespeed", lambda *args, **kwargs: [resultado_rendimiento])

    # Captura el resultado que llega al exportador JSON.
    def _capturar_json(resultado, _path):
        """Guarda el resultado para validar estado de fuentes."""
        capturado["resultado"] = resultado
        return _path

    # Inyecta exportador JSON espía.
    monkeypatch.setattr(cli, "exportar_json", _capturar_json)

    # Inyecta exportadores restantes como no-op.
    monkeypatch.setattr(cli, "exportar_excel", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "exportar_word", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "exportar_pdf", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "exportar_markdown_ia", lambda *args, **kwargs: None)

    # Ejecuta flujo principal.
    codigo = cli.main()

    # Verifica ejecución correcta.
    assert codigo == 0

    # Verifica que PageSpeed no se marque como fuente activa.
    assert "pagespeed" not in capturado["resultado"].fuentes_activas

    # Verifica que PageSpeed sí quede registrado como fuente fallida.
    assert "pagespeed" in capturado["resultado"].fuentes_fallidas
