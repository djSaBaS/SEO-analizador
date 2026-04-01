"""Servicio de composición semántica del informe SEO."""

# Importa anotaciones futuras para tipos autocontenidos.
from __future__ import annotations

# Importa tipos dinámicos para compatibilidad con configuración flexible.
from typing import Any

# Importa constructor de jerarquía visible desacoplado por fuente.
from seo_auditor.documentacion.builders.secciones import construir_jerarquia_visible

# Importa contrato principal de resultados de auditoría.
from seo_auditor.models import ResultadoAuditoria

# Define secciones cuya narrativa depende principalmente de IA.
SECCIONES_DEPENDIENTES_IA = {"Resumen ejecutivo", "Roadmap"}


# Centraliza la construcción del informe como única fuente semántica.
class InformeService:
    """Compone el modelo semántico único para Word, PDF y HTML."""

    # Construye el modelo documental final con metadatos y filtros editoriales.
    def construir_modelo_documental(self, resultado: ResultadoAuditoria, configuracion: Any | None) -> dict[str, Any]:
        """Construye el modelo semántico y aplica reglas condicionales por fuente."""

        # Importa constructor semántico en tiempo de ejecución para evitar ciclos.
        from seo_auditor.reporters.core import construir_modelo_semantico_informe

        # Construye modelo semántico base desde la capa documental.
        modelo = construir_modelo_semantico_informe(resultado)

        # Resuelve flags de disponibilidad por integración.
        gsc_activo = bool(getattr(resultado.search_console, "activo", False))
        ga4_activo = bool(getattr(configuracion, "ga_enabled", getattr(resultado.analytics, "activo", False)))
        ia_activa = bool(getattr(configuracion, "gemini_api_key", "")) or bool(resultado.resumen_ia)

        # Resuelve orden visible de secciones usando builder especializado.
        orden_visible = construir_jerarquia_visible(resultado)

        # Elimina bloques de IA cuando no esté disponible la fuente.
        if not ia_activa:
            orden_visible = [seccion for seccion in orden_visible if seccion not in SECCIONES_DEPENDIENTES_IA]

        # Elimina bloque de comportamiento cuando GA4 esté desactivado.
        if not ga4_activo:
            orden_visible = [seccion for seccion in orden_visible if seccion != "Comportamiento y conversión"]

        # Construye mapa de secciones por título para ordenar de forma estable.
        mapa_secciones = {str(seccion.get("titulo", "")): seccion for seccion in modelo.get("secciones", [])}

        # Conserva portada y anexos fuera del filtro de secciones visibles.
        secciones_fijas = [
            seccion
            for seccion in modelo.get("secciones", [])
            if str(seccion.get("tipo_bloque", "")) in {"portada", "anexo"}
        ]

        # Recompone orden de secciones según jerarquía editorial visible.
        secciones_ordenadas = [mapa_secciones[titulo] for titulo in orden_visible if titulo in mapa_secciones]

        # Guarda la nueva lista en el modelo como fuente única de render.
        modelo["secciones"] = secciones_fijas[:1] + secciones_ordenadas + secciones_fijas[1:]

        # Inserta metadatos editoriales centralizados para todos los exportadores.
        modelo["metadatos_editoriales"] = {
            "orden_secciones": orden_visible,
            "reglas_condicionales": {
                "gsc_activo": gsc_activo,
                "ga4_activo": ga4_activo,
                "ia_activa": ia_activa,
            },
        }

        # Devuelve modelo final listo para render puro.
        return modelo

    # Prepara el paquete integral de informe con modelo semántico y salidas auxiliares.
    def preparar_informe(self, resultado: ResultadoAuditoria, configuracion: Any | None, incluir_markdown_ia: bool = True) -> dict[str, Any]:
        """Prepara el informe completo priorizando el modelo semántico como núcleo."""

        # Obtiene modelo semántico único para todos los formatos finales.
        modelo_documental = self.construir_modelo_documental(resultado, configuracion)

        # Define salida IA auxiliar sin impactar la composición principal.
        markdown_ia_auxiliar = resultado.resumen_ia if incluir_markdown_ia else None

        # Devuelve contrato unificado de preparación de informe.
        return {
            "modelo_semantico": modelo_documental,
            "markdown_ia_auxiliar": markdown_ia_auxiliar,
        }
