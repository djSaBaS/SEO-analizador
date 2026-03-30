# Implementa constructores de secciones y jerarquía en la nueva capa documental.
import re

from seo_auditor.models import ResultadoAuditoria


# Define jerarquía fija obligatoria del informe final.
JERARQUIA_INFORME = [
    "Resumen ejecutivo",
    "KPIs principales",
    "Visibilidad orgánica real",
    "Comportamiento y conversión",
    "Páginas prioritarias",
    "Oportunidades SEO prioritarias",
    "Cruce auditoría técnica + Search Console",
    "Keyword / query mapping inicial",
    "Hallazgos críticos",
    "Quick wins",
    "Acciones técnicas",
    "Acciones de contenido",
    "Rendimiento y experiencia de usuario",
    "Indexación y rastreo",
    "Gestión de indexación",
    "Roadmap",
]

# Define secciones dependientes de Search Console para ocultación condicional.
SECCIONES_GSC = {
    "Visibilidad orgánica real",
    "Oportunidades SEO prioritarias",
    "Cruce auditoría técnica + Search Console",
    "Keyword / query mapping inicial",
}


def _limpiar_markdown_crudo(texto: str) -> str:
    """Limpia markdown frecuente manteniendo el contenido textual."""

    texto_limpio = re.sub(r"^#{1,6}\s*", "", texto, flags=re.MULTILINE)
    texto_limpio = re.sub(r"\*\*(.*?)\*\*", r"\1", texto_limpio)
    texto_limpio = re.sub(r"__(.*?)__", r"\1", texto_limpio)
    texto_limpio = re.sub(r"`([^`]+)`", r"\1", texto_limpio)
    texto_limpio = re.sub(r"^\s*---+\s*$", "", texto_limpio, flags=re.MULTILINE)
    return texto_limpio.strip()


# Devuelve jerarquía visible según fuentes activas de la ejecución.
def construir_jerarquia_visible(resultado: ResultadoAuditoria) -> list[str]:
    """Filtra secciones GSC/Analytics cuando la fuente no está activa."""

    jerarquia = list(JERARQUIA_INFORME)
    if not resultado.search_console.activo:
        jerarquia = [seccion for seccion in jerarquia if seccion not in SECCIONES_GSC]
    if not resultado.analytics.activo:
        jerarquia = [seccion for seccion in jerarquia if seccion != "Comportamiento y conversión"]
    return jerarquia


# Convierte narrativa IA en secciones internas estructuradas.
def construir_secciones_desde_ia(texto_ia: str | None) -> list[dict[str, object]]:
    """Transforma texto IA en secciones semánticas sin markdown crudo."""

    if not texto_ia:
        return []

    texto_limpio = _limpiar_markdown_crudo(texto_ia)
    secciones: list[dict[str, object]] = []
    seccion_actual: dict[str, object] = {"titulo": "Resumen ejecutivo", "tipo": "parrafos", "items": []}

    for linea in texto_limpio.splitlines():
        if not linea.strip():
            continue

        if re.match(r"^(\d+[\).]\s*)?(resumen|kpis|hallazgos|quick wins|acciones técnicas|acciones de contenido|rendimiento|roadmap)", linea.lower()):
            if seccion_actual["items"]:
                secciones.append(seccion_actual)
            titulo = re.sub(r"^\d+[\).]\s*", "", linea).strip().title()
            seccion_actual = {"titulo": titulo, "tipo": "parrafos", "items": []}
            continue

        if linea.startswith(("- ", "* ", "• ")):
            seccion_actual["tipo"] = "vinetas"
            seccion_actual["items"].append(linea[2:].strip())
            continue

        if re.match(r"^\d+[\).]\s+", linea):
            seccion_actual["tipo"] = "numerada"
            seccion_actual["items"].append(re.sub(r"^\d+[\).]\s*", "", linea).strip())
            continue

        if len(linea.strip()) > 220 and ". " in linea:
            for fragmento in [parte.strip() for parte in linea.split(". ") if parte.strip()]:
                seccion_actual["items"].append(fragmento if fragmento.endswith(".") else f"{fragmento}.")
        else:
            seccion_actual["items"].append(linea.strip())

    if seccion_actual["items"]:
        secciones.append(seccion_actual)

    return secciones
