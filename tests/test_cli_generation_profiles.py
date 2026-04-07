# Importa utilidades para fabricar argumentos en pruebas de flujo.
from types import SimpleNamespace

# Importa módulo CLI para validar perfiles y orquestación.
from seo_auditor import cli

# Importa configuración tipada para inyección controlada.
from seo_auditor.config import Configuracion

# Importa modelos mínimos para simular una auditoría válida.
from seo_auditor.models import ResultadoAuditoria, ResultadoUrl


# Construye configuración base reutilizable para pruebas de perfiles.
def _configuracion_base(ga_habilitado: bool = False) -> Configuracion:
    """Devuelve configuración mínima para ejecutar el flujo CLI con mocks."""

    # Devuelve objeto tipado con valores estables.
    return Configuracion(
        gemini_api_key="",
        gemini_model="gemini-2.5-flash",
        pagespeed_api_key="",
        http_timeout=10,
        max_urls=10,
        max_pagepsi_urls=5,
        pagespeed_timeout=45,
        pagespeed_reintentos=1,
        cache_ttl_segundos=60,
        gsc_enabled=False,
        gsc_site_url="",
        gsc_credentials_file="",
        gsc_date_from="",
        gsc_date_to="",
        gsc_row_limit=250,
        ga_enabled=ga_habilitado,
        ga_property_id="123456" if ga_habilitado else "",
        ga_credentials_file="/tmp/falso-ga.json" if ga_habilitado else "",
        ga_date_from="",
        ga_date_to="",
        ga_row_limit=1000,
    )


# Construye un resultado de auditoría mínimo para pruebas de exportación.
def _resultado_base() -> ResultadoAuditoria:
    """Crea un resultado SEO pequeño y estable para evitar dependencias externas."""

    # Devuelve resultado con una URL válida y sin hallazgos.
    return ResultadoAuditoria(
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
        fecha_ejecucion="2026-03-26",
        gestor="Gestor",
    )


# Verifica resolución de perfil para atajo --generar-todo.
def test_resolver_perfil_generacion_generar_todo() -> None:
    """Comprueba que el atajo operativo seleccione el perfil compuesto `todo`."""

    # Construye argumentos mínimos para resolver perfil.
    argumentos = SimpleNamespace(generar_todo=True, modo="completo")

    # Valida perfil compuesto esperado.
    assert cli._resolver_perfil_generacion(argumentos) == "todo"


# Verifica compatibilidad del parser con el nuevo modo compuesto.
def test_parser_acepta_modo_entrega_completa() -> None:
    """Asegura que el parser admita `--modo entrega-completa` sin romper CLI previa."""

    # Crea parser real para validar opciones declaradas.
    parser = cli.crear_parser()

    # Parsea entrada con modo nuevo sin parámetros no relacionados.
    argumentos = parser.parse_args(["--modo", "entrega-completa"])

    # Verifica selección del modo compuesto.
    assert argumentos.modo == "entrega-completa"


# Verifica degradación elegante cuando un exportador SEO falla de forma aislada.
def test_main_exportador_fallido_no_rompe_orquestacion(monkeypatch, tmp_path) -> None:
    """Comprueba que un fallo de exportación aislado no detenga el resto del perfil."""

    # Construye argumentos compatibles con auditoría SEO estándar.
    argumentos = SimpleNamespace(
        sitemap="https://ejemplo.com/sitemap.xml",
        output=str(tmp_path),
        usar_ia=False,
        testia=False,
        testga=False,
        testgsc=False,
        modelo_ia="",
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        gestor="Gestor",
        cliente="",
        max_muestras_ia=5,
        modo="completo",
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
        noGSC=False,
        comparar="periodo-anterior",
        provincia="",
        date_from="",
        date_to="",
        generar_todo=False,
    )

    # Define parser falso para inyectar argumentos controlados.
    class _ParserFalso:
        """Parser mínimo para devolver argumentos simulados."""

        # Devuelve argumentos de prueba sin leer CLI real.
        def parse_args(self):
            """Retorna argumentos fijos para esta prueba."""
            return argumentos

    # Inyecta parser y configuración controlados.
    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())
    monkeypatch.setattr(cli, "cargar_configuracion", lambda: _configuracion_base(ga_habilitado=False))

    # Simula extracción de URLs y auditoría técnica.
    monkeypatch.setattr(cli, "extraer_urls_sitemap", lambda *_args, **_kwargs: ["https://ejemplo.com/"])
    monkeypatch.setattr(cli, "auditar_urls", lambda *_args, **_kwargs: _resultado_base())

    # Simula análisis de indexación para evitar dependencia de red.
    monkeypatch.setattr(cli, "analizar_indexacion_rastreo", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "generar_gestion_indexacion_inteligente", lambda *_args, **_kwargs: [])

    # Registra ejecución de exportadores para comprobar continuidad.
    estado = {"excel": False}

    # Inyecta fallo aislado en JSON.
    monkeypatch.setattr(
        cli, "exportar_json", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("fallo json"))
    )

    # Inyecta exportador Excel funcional para comprobar degradación elegante.
    monkeypatch.setattr(cli, "exportar_excel", lambda *_args, **_kwargs: estado.__setitem__("excel", True))

    # Inyecta resto de exportadores como no-op.
    monkeypatch.setattr(cli, "exportar_word", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "exportar_pdf", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "exportar_html", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "exportar_markdown_ia", lambda *_args, **_kwargs: None)

    # Ejecuta flujo principal del CLI.
    codigo = cli.main()

    # Verifica que la ejecución global finalice correctamente.
    assert codigo == 0

    # Verifica que se ejecutó al menos un exportador tras el fallo inicial.
    assert estado["excel"] is True


# Verifica que el perfil `todo` incluya GA4 premium cuando GA4 esté habilitado.
def test_main_generar_todo_invoca_ga4_premium(monkeypatch, tmp_path) -> None:
    """Comprueba que el orquestador compuesto dispare GA4 premium sin segunda auditoría."""

    # Construye argumentos para activar el atajo --generar-todo.
    argumentos = SimpleNamespace(
        sitemap="https://ejemplo.com/sitemap.xml",
        output=str(tmp_path),
        usar_ia=False,
        testia=False,
        testga=False,
        testgsc=False,
        modelo_ia="",
        pagepsi="",
        pagepsi_list="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        gestor="Gestor",
        cliente="Cliente Demo",
        max_muestras_ia=5,
        modo="completo",
        modo_rapido=False,
        cache_ttl=0,
        invalidar_cache=False,
        noGSC=False,
        comparar="periodo-anterior",
        provincia="Madrid",
        date_from="2026-02-01",
        date_to="2026-02-28",
        generar_todo=True,
    )

    # Define parser falso para inyección estable.
    class _ParserFalso:
        """Parser mínimo para devolver argumentos simulados."""

        # Devuelve argumentos preparados para esta prueba.
        def parse_args(self):
            """Retorna argumentos fijos."""
            return argumentos

    # Inyecta parser y configuración con GA4 habilitado.
    monkeypatch.setattr(cli, "crear_parser", lambda: _ParserFalso())
    monkeypatch.setattr(cli, "cargar_configuracion", lambda: _configuracion_base(ga_habilitado=True))

    # Simula extracción de URLs y auditoría técnica.
    monkeypatch.setattr(cli, "extraer_urls_sitemap", lambda *_args, **_kwargs: ["https://ejemplo.com/"])
    monkeypatch.setattr(cli, "auditar_urls", lambda *_args, **_kwargs: _resultado_base())
    monkeypatch.setattr(cli, "analizar_indexacion_rastreo", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "generar_gestion_indexacion_inteligente", lambda *_args, **_kwargs: [])

    # Inyecta exportadores SEO como no-op.
    monkeypatch.setattr(cli, "exportar_json", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "exportar_excel", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "exportar_word", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "exportar_pdf", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "exportar_html", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(cli, "exportar_markdown_ia", lambda *_args, **_kwargs: None)

    # Registra invocación del generador premium.
    estado = {"premium": False}

    # Simula salida exitosa del informe premium.
    def _premium(*_args, **_kwargs):
        """Marca ejecución y devuelve metadatos mínimos de salida."""
        estado["premium"] = True
        return {"activo": True, "html": "a.html", "pdf": "a.pdf", "excel": "a.xlsx"}

    # Inyecta generador premium simulado.
    monkeypatch.setattr(cli, "generar_informe_ga4_premium", _premium)

    # Ejecuta flujo principal del CLI.
    codigo = cli.main()

    # Verifica finalización correcta del flujo compuesto.
    assert codigo == 0

    # Verifica invocación de GA4 premium dentro del perfil todo.
    assert estado["premium"] is True
