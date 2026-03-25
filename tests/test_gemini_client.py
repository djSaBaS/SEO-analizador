# Importa Path para validar coherencia del archivo de prompt.
from pathlib import Path

# Importa módulo bajo prueba.
from seo_auditor import gemini_client
from seo_auditor.models import MetricaGscPagina, ResultadoAuditoria


# Verifica que el fallback interno replique el archivo editable.
def test_prompt_fallback_coincide_con_archivo_externo() -> None:
    """Comprueba consistencia total entre fallback y plantilla externa."""

    # Lee el archivo real del prompt editable del repositorio.
    prompt_archivo = Path("Prompt/consulta_ia_prompt.txt").read_text(encoding="utf-8")

    # Asegura que ambos contenidos sean idénticos para evitar divergencias.
    assert gemini_client.PROMPT_IA_FALLBACK == prompt_archivo


# Verifica que errores de lectura usen fallback sin romper ejecución.
def test_cargar_plantilla_prompt_ia_usa_fallback_si_hay_oserror(monkeypatch) -> None:
    """Confirma fallback seguro cuando la lectura del archivo falla."""

    # Simula objeto ruta que existe pero falla al leer contenido.
    class RutaInaccesible:
        """Representa una ruta con error de permisos de lectura."""

        # Simula que la ruta es un archivo regular.
        def is_file(self) -> bool:
            return True

        # Lanza error de sistema equivalente a permisos/IO.
        def read_text(self, encoding: str) -> str:
            raise OSError("Permiso denegado")

    # Inyecta ruta inaccesible para forzar el camino de fallback.
    monkeypatch.setattr(gemini_client, "RUTA_PROMPT_IA", RutaInaccesible())

    # Ejecuta carga de plantilla con ruta simulada.
    plantilla = gemini_client.cargar_plantilla_prompt_ia()

    # Verifica que se devuelva el fallback interno y no se lance excepción.
    assert plantilla == gemini_client.PROMPT_IA_FALLBACK


# Verifica reemplazo robusto sin interpretar llaves ajenas al placeholder.
def test_construir_prompt_ia_no_rompe_con_llaves_literales() -> None:
    """Asegura que solo se sustituya `{datos_json}` y se preserven otras llaves."""

    # Construye plantilla con llaves literales adicionales comunes en prompts.
    plantilla = "Ejemplo {json} literal\nPayload:\n{datos_json}"

    # Construye datos mínimos para serialización controlada.
    datos = {"clave": "valor"}

    # Genera prompt final desde la plantilla editable.
    prompt = gemini_client.construir_prompt_ia(plantilla, datos)

    # Verifica que llaves literales se mantengan intactas.
    assert "{json}" in prompt

    # Verifica que se inserte el JSON real de auditoría.
    assert '"clave": "valor"' in prompt


# Verifica que se exija el marcador obligatorio de datos.
def test_construir_prompt_ia_falla_si_no_existe_placeholder() -> None:
    """Evita enviar consultas sin datos de auditoría por error de plantilla."""

    # Define plantilla inválida sin marcador de datos.
    plantilla = "Prompt sin datos"

    # Verifica error explícito al componer prompt sin placeholder.
    try:
        gemini_client.construir_prompt_ia(plantilla, {"x": 1})
        assert False, "Se esperaba ValueError al faltar {datos_json}."
    except ValueError as exc:
        # Confirma que el mensaje indique claramente el problema.
        assert "{datos_json}" in str(exc)


# Verifica que el contexto IA incluya flags explícitos de fuentes activas.
def test_construir_contexto_ia_incluye_banderas_fuentes() -> None:
    """Comprueba la presencia de banderas para evitar contradicciones narrativas."""

    # Construye auditoría mínima con GSC activo.
    auditoria = ResultadoAuditoria(
        sitemap="https://ejemplo.com/sitemap.xml",
        total_urls=1,
        resultados=[],
        cliente="Ejemplo",
        fecha_ejecucion="2026-03-25",
        gestor="Gestor",
        fuentes_activas=["search_console"],
    )
    auditoria.search_console.activo = True
    auditoria.search_console.paginas = [
        MetricaGscPagina(url="https://ejemplo.com", clicks=12, impresiones=300, ctr=0.04, posicion_media=9.4)
    ]

    # Construye contexto para IA.
    contexto = gemini_client.construir_contexto_ia(auditoria, max_muestras=10)

    # Verifica banderas clave para prompt robusto.
    assert contexto["gsc_activo"] is True
    assert contexto["usar_seccion_gsc"] is True
    assert "search_console" in contexto["fuentes_activas"]


# Verifica que el texto IA elimine contradicciones cuando GSC está activo.
def test_validar_consistencia_resumen_ia_filtra_frases_contradictorias() -> None:
    """Evita frases incorrectas sobre ausencia de GSC si la fuente está activa."""

    # Simula respuesta IA con frase contradictoria.
    texto = "Aunque no se proporcionan datos específicos de GSC, se detectan oportunidades."

    # Aplica validador con contexto de GSC activo.
    salida = gemini_client.validar_consistencia_resumen_ia(texto, {"gsc_activo": True, "gsc": {"clics_totales": 10, "impresiones_totales": 100}})

    # Verifica eliminación de la frase incorrecta.
    assert "no se proporcionan datos específicos de gsc" not in salida.lower()


# Verifica coherencia usando también la lista de fuentes activas.
def test_validar_consistencia_resumen_ia_respeta_fuentes_activas() -> None:
    """Garantiza limpieza de negaciones cuando Search Console está en fuentes activas."""

    # Simula respuesta IA contradictoria heredada.
    texto = "Sin datos de Search Console en esta ejecución."

    # Ejecuta validación con fuente activa aunque gsc_activo no venga explícito.
    salida = gemini_client.validar_consistencia_resumen_ia(
        texto,
        {"fuentes_activas": ["search_console"], "gsc": {"clics_totales": 14, "impresiones_totales": 450}},
    )

    # Comprueba eliminación de contradicción con fuente activa.
    assert "sin datos de search console" not in salida.lower()


# Verifica que no se altere el texto cuando GSC no está activo.
def test_validar_consistencia_resumen_ia_conserva_texto_sin_gsc() -> None:
    """Confirma que las frases de ausencia se mantengan cuando GSC no está activo."""

    # Define texto legítimo de ausencia de datos GSC.
    texto = "No se proporcionan datos específicos de GSC en esta ejecución."

    # Ejecuta validación sin fuente activa de Search Console.
    salida = gemini_client.validar_consistencia_resumen_ia(texto, {"gsc_activo": False, "fuentes_activas": []})

    # Verifica que el mensaje permanezca sin cambios.
    assert salida == texto
