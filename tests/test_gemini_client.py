# Importa Path para validar coherencia del archivo de prompt.
from pathlib import Path

# Importa módulo bajo prueba.
from seo_auditor import gemini_client


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
