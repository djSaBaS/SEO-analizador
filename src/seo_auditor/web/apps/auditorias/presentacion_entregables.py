"""Utilidades de presentación de entregables para la capa web interna."""

# Importa Path para trabajar rutas de archivos de forma segura.
from pathlib import Path

# Importa tipos para contratos explícitos de entrada/salida.
from typing import Any

# Define catálogo de metadatos de presentación por identificador técnico.
CATALOGO_ENTREGABLES: dict[str, dict[str, str]] = {
    "json_tecnico": {"nombre": "JSON técnico", "descripcion": "Datos técnicos completos"},
    "excel_seo": {"nombre": "Informe Excel SEO", "descripcion": "KPIs y dashboard"},
    "word_seo": {"nombre": "Informe Word SEO", "descripcion": "Documento ejecutivo"},
    "pdf_seo": {"nombre": "Informe PDF SEO", "descripcion": "PDF ejecutivo"},
    "html_seo": {"nombre": "Informe HTML SEO", "descripcion": "Versión navegable"},
    "markdown_ia": {"nombre": "Markdown IA", "descripcion": "Salida narrativa IA"},
    "ga4_premium": {"nombre": "Informe GA4 premium", "descripcion": "Informe avanzado de analítica"},
}

# Define estados legibles para UI a partir del estado técnico.
ESTADOS_LEGIBLES: dict[str, str] = {
    "generado": "Generado",
    "omitido": "Omitido",
    "error_no_fatal": "Error no fatal",
}

# Define extensiones consideradas entregables principales en dashboard.
EXTENSIONES_PRINCIPALES = {".pdf", ".docx", ".xlsx", ".html", ".htm", ".json", ".md"}


# Convierte tamaño en bytes a formato legible para humanos.
def formatear_tamano_archivo(bytes_totales: int) -> str:
    """Devuelve tamaño legible en B, KB, MB o GB con formato compacto."""

    # Devuelve fallback cuando el tamaño no es válido.
    if bytes_totales < 0:
        return "Tamaño no disponible"

    # Devuelve bytes en formato directo cuando es pequeño.
    if bytes_totales < 1024:
        return f"{bytes_totales} B"

    # Convierte a kilobytes para valores intermedios.
    if bytes_totales < 1024 * 1024:
        return f"{bytes_totales / 1024:.1f} KB"

    # Convierte a megabytes para valores habituales de entregables.
    if bytes_totales < 1024 * 1024 * 1024:
        return f"{bytes_totales / (1024 * 1024):.1f} MB"

    # Convierte a gigabytes para valores excepcionales.
    return f"{bytes_totales / (1024 * 1024 * 1024):.1f} GB"


# Devuelve metadatos amigables del entregable según su identificador técnico.
def resolver_metadatos_entregable(entregable: str) -> dict[str, str]:
    """Obtiene nombre y descripción de UI para un entregable concreto."""

    # Busca metadatos definidos para el entregable indicado.
    metadatos = CATALOGO_ENTREGABLES.get(entregable, {})

    # Devuelve nombre amigable o fallback derivado del identificador.
    nombre = metadatos.get("nombre") or entregable.replace("_", " ").strip().title()

    # Devuelve descripción amigable o fallback genérico.
    descripcion = metadatos.get("descripcion") or "Entregable generado"

    # Devuelve metadatos resueltos para consumo de UI.
    return {"nombre": nombre, "descripcion": descripcion}


# Enriquecer un registro técnico con datos legibles para la tabla web.
def enriquecer_registro_entregable(registro: dict[str, Any]) -> dict[str, Any]:
    """Añade nombre amigable, estado legible y detalle útil para la interfaz web."""

    # Crea copia para no mutar estructura original recibida.
    salida = dict(registro)

    # Resuelve identificador técnico base del entregable.
    entregable = str(registro.get("entregable") or "").strip()

    # Resuelve estado técnico del registro.
    estado = str(registro.get("estado") or "").strip()

    # Resuelve ruta final registrada por el proceso de exportación.
    ruta_final = str(registro.get("ruta_final") or "").strip()

    # Obtiene metadatos amigables para el entregable actual.
    metadatos = resolver_metadatos_entregable(entregable)

    # Expone nombre amigable en la salida para la tabla web.
    salida["nombre_amigable"] = metadatos["nombre"]

    # Expone estado legible para mejorar experiencia de usuario.
    salida["estado_legible"] = ESTADOS_LEGIBLES.get(estado, estado or "Sin estado")

    # Conserva el detalle técnico existente cuando venga informado.
    detalle_original = str(registro.get("detalle") or "").strip()

    # En estado generado construye detalle útil por defecto.
    if estado == "generado":
        # Inicializa detalle con descripción funcional del entregable.
        detalle_generado = metadatos["descripcion"]

        # Intenta resolver tamaño cuando la ruta final apunta a archivo real.
        if ruta_final:
            # Construye ruta candidata para lectura de metadatos.
            ruta_archivo = Path(ruta_final)

            # Verifica que la ruta exista y sea archivo regular.
            if ruta_archivo.exists() and ruta_archivo.is_file():
                # Obtiene tamaño en bytes del archivo generado.
                tamano_bytes = ruta_archivo.stat().st_size

                # Añade tamaño legible al detalle para mayor contexto.
                detalle_generado = f"{detalle_generado} · {formatear_tamano_archivo(tamano_bytes)}"

        # Asigna detalle enriquecido para entregables generados.
        salida["detalle_mostrable"] = detalle_generado

        # Devuelve salida enriquecida para estado generado.
        return salida

    # En omitido/error mantiene detalle original cuando exista.
    if detalle_original:
        # Asigna detalle original como mensaje principal.
        salida["detalle_mostrable"] = detalle_original

        # Devuelve salida enriquecida conservando trazabilidad.
        return salida

    # Usa fallback legible cuando no exista detalle explícito.
    salida["detalle_mostrable"] = "Sin detalle adicional"

    # Devuelve salida enriquecida para estados no generados.
    return salida


# Enriquecer una colección completa de registros para su uso en web.
def enriquecer_registros_entregables(registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transforma registros técnicos a formato legible para tabla de descargas."""

    # Devuelve lista enriquecida aplicando transformación uno a uno.
    return [enriquecer_registro_entregable(registro) for registro in list(registros or [])]


# Determina si un archivo pertenece al conjunto de entregables principales.
def es_documento_principal(ruta: Path) -> bool:
    """Evalúa si una ruta corresponde a un documento principal para dashboard."""

    # Obtiene extensión en minúsculas para comparación estable.
    extension = ruta.suffix.lower().strip()

    # Excluye archivos sin extensión o no listados como principales.
    if extension not in EXTENSIONES_PRINCIPALES:
        return False

    # Excluye marcadores temporales y artefactos auxiliares obvios.
    if ruta.name.lower().startswith("aux"):
        return False

    # Marca como principal cuando supera filtros de tipo.
    return True
