"""Servicio de orquestación de entregables y perfiles de generación."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Callable

from seo_auditor.models import EstadoEntregable, RegistroEntregable, ResultadoEntregables

ENTREGABLE_JSON_TECNICO = "json_tecnico"
ENTREGABLE_EXCEL_SEO = "excel_seo"
ENTREGABLE_WORD_SEO = "word_seo"
ENTREGABLE_PDF_SEO = "pdf_seo"
ENTREGABLE_HTML_SEO = "html_seo"
ENTREGABLE_MARKDOWN_IA = "markdown_ia"
ENTREGABLE_GA4_PREMIUM = "ga4_premium"

ENTREGABLES_BASE_AUDITORIA = [
    ENTREGABLE_JSON_TECNICO,
    ENTREGABLE_EXCEL_SEO,
    ENTREGABLE_WORD_SEO,
    ENTREGABLE_PDF_SEO,
    ENTREGABLE_HTML_SEO,
    ENTREGABLE_MARKDOWN_IA,
]

PERFILES_GENERACION: dict[str, list[str]] = {
    "auditoria-seo-completa": ENTREGABLES_BASE_AUDITORIA,
    "todo": ENTREGABLES_BASE_AUDITORIA + [ENTREGABLE_GA4_PREMIUM],
    "solo-ga4-premium": [ENTREGABLE_GA4_PREMIUM],
}


@dataclass(slots=True)
class ModeloEntregables:
    """Datos de entrada ya preparados para exportadores documentales."""

    carpeta_base_salida: Path
    carpeta_salida: Path
    fecha_ejecucion: str
    entregables_solicitados: list[str]
    cliente_preferido: str
    sitemap: str
    gestor: str
    periodo_desde: str
    periodo_hasta: str
    comparacion_ga4: str = "periodo-anterior"
    provincia_ga4: str = ""


@dataclass(slots=True)
class EntregablesAdapters:
    """Dependencias inyectables para exportación desacoplada de entregables."""

    exportar_json: Callable[..., Path]
    exportar_excel: Callable[..., Path]
    exportar_word: Callable[..., Path]
    exportar_pdf: Callable[..., Path]
    exportar_html: Callable[..., Path]
    exportar_markdown_ia: Callable[..., Path | None]
    generar_informe_ga4_premium: Callable[..., dict[str, Any]]
    resolver_cliente_informe_ga4: Callable[[str | None, str | None], str]
    iterar_con_progreso: Callable[..., Any]


class EntregablesService:
    """Centraliza la generación de entregables estándar y premium."""

    def __init__(self, adapters: EntregablesAdapters) -> None:
        self.adapters = adapters
        self.logger = logging.getLogger(__name__)

    def generar_entregables(self, resultado: Any, modelo_documental: ModeloEntregables, configuracion: Any) -> ResultadoEntregables:
        """Orquesta la exportación y devuelve un resumen estructurado consumible por CLI/web."""
        resumen = ResultadoEntregables()

        exportadores = {
            ENTREGABLE_JSON_TECNICO: self.adapters.exportar_json,
            ENTREGABLE_EXCEL_SEO: self.adapters.exportar_excel,
            ENTREGABLE_WORD_SEO: self.adapters.exportar_word,
            ENTREGABLE_PDF_SEO: self.adapters.exportar_pdf,
            ENTREGABLE_HTML_SEO: self.adapters.exportar_html,
            ENTREGABLE_MARKDOWN_IA: self.adapters.exportar_markdown_ia,
        }

        for entregable in self.adapters.iterar_con_progreso(modelo_documental.entregables_solicitados, "Exportación", "archivo"):
            if entregable in exportadores:
                self._exportar_entregable_estandar(resumen, entregable, exportadores[entregable], resultado, modelo_documental)
                continue

            if entregable == ENTREGABLE_GA4_PREMIUM:
                self._exportar_entregable_ga4_premium(resumen, modelo_documental, configuracion)
                continue

            self._registrar_omitido(resumen, entregable, "no reconocido")

        return resumen

    def _exportar_entregable_estandar(
        self,
        resumen: ResultadoEntregables,
        entregable: str,
        exportador: Callable[..., Path | None],
        resultado: Any,
        modelo_documental: ModeloEntregables,
    ) -> None:
        try:
            ruta = exportador(resultado, modelo_documental.carpeta_salida)
            self._registrar_generado(resumen, entregable, ruta)
        except Exception as exc:
            self._registrar_error(resumen, entregable, exc)

    def _exportar_entregable_ga4_premium(self, resumen: ResultadoEntregables, modelo_documental: ModeloEntregables, configuracion: Any) -> None:
        if not configuracion.ga_enabled:
            self._registrar_omitido(resumen, ENTREGABLE_GA4_PREMIUM, "GA4 no habilitado")
            return

        carpeta_premium = modelo_documental.carpeta_base_salida / "ga4_premium" / modelo_documental.fecha_ejecucion
        try:
            cliente = self.adapters.resolver_cliente_informe_ga4(
                modelo_documental.cliente_preferido,
                modelo_documental.sitemap,
            )
        except Exception as exc:
            self._registrar_error(resumen, ENTREGABLE_GA4_PREMIUM, exc)
            return
        try:
            salida = self.adapters.generar_informe_ga4_premium(
                configuracion,
                carpeta_premium,
                cliente,
                modelo_documental.gestor,
                modelo_documental.periodo_desde,
                modelo_documental.periodo_hasta,
                modelo_documental.comparacion_ga4,
                modelo_documental.provincia_ga4,
            )
        except Exception as exc:
            self._registrar_error(resumen, ENTREGABLE_GA4_PREMIUM, exc)
            return

        if not salida.get("activo", False):
            self._registrar_omitido(resumen, ENTREGABLE_GA4_PREMIUM, salida.get("error", "sin detalle de error"))
            return

        rutas = [salida.get("html"), salida.get("pdf"), salida.get("excel")]
        ruta_final = " | ".join(str(ruta) for ruta in rutas if ruta)
        self._registrar_generado(resumen, ENTREGABLE_GA4_PREMIUM, ruta_final)

    def _registrar_generado(self, resumen: ResultadoEntregables, entregable: str, ruta: Path | str | None) -> None:
        ruta_final = str(ruta or "")
        resumen.generados.append(entregable)
        resumen.registros.append(
            RegistroEntregable(entregable=entregable, estado=EstadoEntregable.GENERADO, ruta_final=ruta_final)
        )

    def _registrar_omitido(self, resumen: ResultadoEntregables, entregable: str, detalle: str) -> None:
        mensaje = f"{entregable} ({detalle})"
        resumen.omitidos.append(mensaje)
        resumen.registros.append(RegistroEntregable(entregable=entregable, estado=EstadoEntregable.OMITIDO, detalle=detalle))

    def _registrar_error(self, resumen: ResultadoEntregables, entregable: str, exc: Exception) -> None:
        detalle = str(exc)
        resumen.errores_no_fatales.append(f"{entregable}: {detalle}")
        resumen.registros.append(
            RegistroEntregable(entregable=entregable, estado=EstadoEntregable.ERROR_NO_FATAL, detalle=detalle)
        )
        self.logger.warning("No se pudo exportar %s: %s", entregable, detalle)
