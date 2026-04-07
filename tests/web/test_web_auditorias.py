# Importa sistema para configurar settings de Django en pruebas.
import os

# Importa fechas para construir payload de formulario.
from datetime import date, timedelta

# Importa utilidades de mock para aislar llamadas al núcleo real.
from unittest.mock import MagicMock, patch

# Importa bootstrap de Django para pruebas de vistas.
import django

# Importa cliente de pruebas HTTP de Django.
from django.test import Client

# Define módulo de configuración Django para esta suite.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seo_auditor.web.config.settings")

# Inicializa Django para habilitar URLs y formularios.
django.setup()

# Verifica que el dashboard responde correctamente en GET.
def test_dashboard_carga_correctamente():
    """Comprueba que la vista dashboard responde HTTP 200."""

    # Crea cliente de pruebas para peticiones locales.
    cliente = Client()

    # Simula que no existen ejecuciones para evitar acceso real a BD.
    with patch("seo_auditor.web.apps.auditorias.views.EjecucionAuditoria.objects") as objetos_mock:
        # Devuelve lista vacía en slicing de queryset simulado.
        objetos_mock.all.return_value.__getitem__.return_value = []

        # Ejecuta petición GET sobre la raíz del sitio web.
        respuesta = cliente.get("/")

    # Verifica código de respuesta exitoso.
    assert respuesta.status_code == 200


# Verifica validación de fechas incorrectas en el formulario.
def test_formulario_rechaza_periodo_invertido():
    """Comprueba que el formulario rechaza fecha fin anterior o igual."""

    # Importa formulario localmente tras bootstrap de Django.
    from seo_auditor.web.apps.auditorias.forms import NuevaAuditoriaForm

    # Define hoy para construir fechas deterministas.
    hoy = date.today()

    # Construye formulario con periodo invertido inválido.
    formulario = NuevaAuditoriaForm(
        data={
            "sitemap": "https://ejemplo.com/sitemap.xml",
            "cliente": "Cliente Demo",
            "gestor": "Gestor Demo",
            "fecha_inicio": hoy.isoformat(),
            "fecha_fin": hoy.isoformat(),
            "modo_informe": "completo",
        }
    )

    # Verifica que la validación global marque el formulario inválido.
    assert not formulario.is_valid()

    # Verifica que el error se asigne al campo esperado.
    assert "fecha_fin" in formulario.errors


# Verifica construcción de request interno desde formulario validado.
def test_construccion_request_web_reutiliza_contrato_nucleo():
    """Comprueba que el adaptador web genera un `AuditoriaRequest` coherente."""

    # Importa adaptador localmente tras bootstrap de Django.
    from seo_auditor.web.apps.auditorias.services_web import (
        construir_request_desde_formulario,
    )

    # Define fecha actual para construir ventana válida.
    hoy = date.today()

    # Define fecha inicial separada un día para regla de negocio.
    ayer = hoy - timedelta(days=1)

    # Construye request a partir de datos limpios simulados.
    request = construir_request_desde_formulario(
        {
            "sitemap": "https://ejemplo.com/sitemap.xml",
            "cliente": "Cliente Demo",
            "gestor": "Gestor Demo",
            "fecha_inicio": ayer,
            "fecha_fin": hoy,
            "usar_ia": True,
            "modo_informe": "resumen",
            "pagepsi_url": "",
            "generar_todo": True,
            "modo_rapido": False,
            "cache_ttl": 60,
        }
    )

    # Verifica que el request respeta sitemap ingresado.
    assert request.sitemap == "https://ejemplo.com/sitemap.xml"

    # Verifica que el modo de informe se transfiera correctamente.
    assert request.informe.modo == "resumen"

    # Verifica que el perfil de generación completo quede activo.
    assert request.informe.perfil_generacion == "todo"


# Verifica flujo de creación y render de detalle con ejecución simulada.
def test_vista_nueva_auditoria_ejecuta_y_redirige():
    """Comprueba que POST válido crea ejecución y redirige a detalle."""

    # Crea cliente de pruebas para enviar formulario.
    cliente = Client()

    # Define fechas válidas para ejecución de prueba.
    hoy = date.today()

    # Define fecha inicial coherente con regla de periodo.
    ayer = hoy - timedelta(days=1)

    # Define payload mínimo del formulario web.
    payload = {
        "sitemap": "https://ejemplo.com/sitemap.xml",
        "cliente": "Cliente Demo",
        "gestor": "Gestor Demo",
        "fecha_inicio": ayer.isoformat(),
        "fecha_fin": hoy.isoformat(),
        "usar_ia": "on",
        "modo_informe": "completo",
        "pagepsi_url": "",
        "generar_todo": "on",
        "modo_rapido": "",
        "cache_ttl": "0",
    }

    # Crea stub de ejecución para simular persistencia sin base de datos.
    ejecucion_mock = MagicMock()

    # Define identificador usado en redirección y detalle.
    ejecucion_mock.pk = 7

    # Define id para interpolación de ruta de detalle.
    ejecucion_mock.id = 7

    # Define lista de entregables serializados para render de detalle.
    ejecucion_mock.entregables = [
        {"entregable": "json_tecnico", "estado": "generado", "ruta_final": __file__, "detalle": ""}
    ]

    # Define estructura mínima de resumen para plantilla de detalle.
    ejecucion_mock.resumen_resultado = {
        "auditoria": {"fecha_ejecucion": hoy.isoformat(), "paginas_prioritarias": [], "quick_wins": []}
    }

    # Define metadatos básicos usados en detalle.
    ejecucion_mock.cliente = "Cliente Demo"
    ejecucion_mock.sitemap = "https://ejemplo.com/sitemap.xml"
    ejecucion_mock.gestor = "Gestor Demo"
    ejecucion_mock.fecha_inicio = ayer
    ejecucion_mock.fecha_fin = hoy
    ejecucion_mock.fuentes_activas = ["pagespeed"]
    ejecucion_mock.fuentes_fallidas = []
    ejecucion_mock.ruta_salida = __file__
    ejecucion_mock.mensaje_error = ""

    # Simula display de estado para plantilla de detalle.
    ejecucion_mock.get_estado_display.return_value = "Finalizada"

    # Simula encolado asíncrono para evitar ejecución pesada real.
    with (
        patch("seo_auditor.web.apps.auditorias.views.EjecucionAuditoria.objects") as objetos_mock,
        patch(
            "seo_auditor.web.apps.auditorias.views._lanzar_auditoria_en_segundo_plano",
            return_value=MagicMock(),
        ) as lanzar_mock,
    ):
        # Configura creación de ejecución en POST.
        objetos_mock.create.return_value = ejecucion_mock

        # Ejecuta POST del formulario para crear auditoría.
        respuesta = cliente.post("/auditorias/nueva/", data=payload)

        # Verifica que el flujo envía la ejecución al hilo de trabajo.
        lanzar_mock.assert_called_once()

        # Configura recuperación por id para vista de detalle.
        objetos_mock.get.return_value = ejecucion_mock

        # Carga pantalla de detalle para validar render básico.
        detalle = cliente.get("/auditorias/7/")

    # Verifica redirección tras finalizar el flujo.
    assert respuesta.status_code == 302

    # Verifica respuesta exitosa de la vista de detalle.
    assert detalle.status_code == 200

    # Verifica que el enlace de descarga esté presente en HTML.
    assert "Descargar" in detalle.content.decode("utf-8")


# Verifica que la vista detalle muestre prioridades y quick wins cuando existen.
def test_detalle_muestra_prioridades_y_quick_wins_reales():
    """Comprueba que la plantilla no use fallback si hay datos reales disponibles."""

    # Crea cliente de pruebas para consultar vista de detalle.
    cliente = Client()

    # Construye ejecución simulada con datos reales de priorización.
    ejecucion_mock = MagicMock()

    # Define identificador de la ejecución simulada.
    ejecucion_mock.id = 11

    # Define datos básicos de cabecera de ejecución.
    ejecucion_mock.cliente = "Cliente Demo"
    ejecucion_mock.sitemap = "https://ejemplo.com/sitemap.xml"
    ejecucion_mock.gestor = "Gestor Demo"
    ejecucion_mock.fecha_inicio = date.today() - timedelta(days=1)
    ejecucion_mock.fecha_fin = date.today()
    ejecucion_mock.fuentes_activas = ["sitemap"]
    ejecucion_mock.fuentes_fallidas = []
    ejecucion_mock.fuentes_incompatibles = []
    ejecucion_mock.ruta_salida = ""
    ejecucion_mock.mensaje_error = ""
    ejecucion_mock.entregables = []

    # Define estado legible para plantilla.
    ejecucion_mock.get_estado_display.return_value = "Finalizada"

    # Define resumen con prioridades y quick wins poblados.
    ejecucion_mock.resumen_resultado = {
        "auditoria": {
            "fecha_ejecucion": "2026-04-03",
            "seo_score_global": 73.2,
            "score_tecnico": 70.1,
            "score_contenido": 75.9,
            "resumen_ia": "Resumen de prueba.",
            "paginas_prioritarias": [
                {
                    "url": "https://ejemplo.com/landing",
                    "prioridad_score": 85.0,
                    "motivos": ["CTR bajo", "alto potencial"],
                },
            ],
            "quick_wins": [
                {
                    "url": "https://ejemplo.com/landing",
                    "problemas": ["Meta description corta"],
                    "recomendaciones": ["Ampliar a 140-160 caracteres"],
                },
            ],
        }
    }

    # Simula acceso al ORM para devolver la ejecución preparada.
    with patch("seo_auditor.web.apps.auditorias.views.EjecucionAuditoria.objects") as objetos_mock:
        # Configura recuperación por id para la vista detalle.
        objetos_mock.get.return_value = ejecucion_mock

        # Ejecuta petición de detalle sobre la ejecución simulada.
        respuesta = cliente.get("/auditorias/11/")

    # Decodifica HTML para realizar aserciones legibles.
    contenido = respuesta.content.decode("utf-8")

    # Verifica estado de respuesta correcto.
    assert respuesta.status_code == 200

    # Verifica que se muestre URL prioritaria real.
    assert "https://ejemplo.com/landing" in contenido

    # Verifica que se muestre recomendación de quick win real.
    assert "Ampliar a 140-160 caracteres" in contenido

    # Verifica que no se renderice fallback vacío de prioridades.
    assert "No se han detectado páginas prioritarias." not in contenido

    # Verifica que no se renderice fallback vacío de quick wins.
    assert "No se han detectado quick wins." not in contenido


# Verifica que el listado de dashboard ignora archivos de caché.
def test_listado_recientes_excluye_cache(tmp_path, monkeypatch):
    """Comprueba que `_listar_archivos_recientes` no devuelve artefactos de `.cache`."""

    # Importa helper de listado desde vistas web.
    from seo_auditor.web.apps.auditorias.views import _listar_archivos_recientes

    # Crea carpeta raíz de salidas de prueba.
    carpeta_salidas = tmp_path / "salidas"

    # Crea carpeta de caché simulada del núcleo.
    carpeta_cache = carpeta_salidas / ".cache" / "pagespeed"

    # Crea carpeta de cliente con archivo visible.
    carpeta_cliente = carpeta_salidas / "cliente" / "2026-04-02"

    # Crea estructura de directorios necesaria.
    carpeta_cache.mkdir(parents=True)

    # Crea estructura de directorios visible en dashboard.
    carpeta_cliente.mkdir(parents=True)

    # Escribe archivo de caché que no debe listarse.
    (carpeta_cache / "cache.json").write_text("{}", encoding="utf-8")

    # Escribe archivo de informe que sí debe listarse.
    (carpeta_cliente / "informe.html").write_text("ok", encoding="utf-8")

    # Cambia directorio de trabajo para usar la ruta relativa `./salidas`.
    monkeypatch.chdir(tmp_path)

    # Ejecuta listado de archivos recientes del dashboard.
    recientes = _listar_archivos_recientes(limite=10)

    # Verifica que solo aparece el archivo visible y no el de caché.
    assert any(item["nombre"] == "informe.html" for item in recientes)

    # Verifica que no se expone archivo dentro de `.cache`.
    assert all(".cache" not in item["ruta"] for item in recientes)


# Verifica que no se permitan descargas fuera de la carpeta de salidas.
def test_descarga_bloquea_path_traversal(tmp_path, monkeypatch):
    """Comprueba que la vista de descarga rechace rutas fuera de `./salidas`."""

    # Crea cliente de pruebas para endpoint de descarga.
    cliente = Client()

    # Crea archivo fuera de `./salidas` que no debe poder descargarse.
    archivo_externo = tmp_path / "secreto.txt"
    archivo_externo.write_text("secreto", encoding="utf-8")

    # Simula ejecución con registro de entregable apuntando fuera de salidas.
    ejecucion_mock = MagicMock()
    ejecucion_mock.entregables = [
        {"entregable": "json_tecnico", "estado": "generado", "ruta_final": str(archivo_externo), "detalle": ""}
    ]

    # Cambia directorio para que `./salidas` apunte al tmp de la prueba.
    monkeypatch.chdir(tmp_path)

    # Simula recuperación ORM de la ejecución objetivo.
    with patch("seo_auditor.web.apps.auditorias.views.EjecucionAuditoria.objects") as objetos_mock:
        # Devuelve ejecución simulada para la vista.
        objetos_mock.get.return_value = ejecucion_mock

        # Ejecuta petición de descarga sobre índice existente.
        respuesta = cliente.get("/auditorias/1/descargar/0/")

    # Verifica que la descarga sea rechazada por seguridad.
    assert respuesta.status_code == 404
