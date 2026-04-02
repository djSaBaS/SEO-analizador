"""Servicios adaptadores entre la capa web Django y el núcleo de auditoría."""

# Importa serialización de dataclasses para persistencia ligera.
from dataclasses import asdict

# Importa espacio de nombres simple para compatibilidad con request legado.
from types import SimpleNamespace

# Importa typing para contratos explícitos en el adaptador web.
from typing import Any

# Importa configuración global del núcleo para reusar integraciones.
from seo_auditor.config import cargar_configuracion

# Importa contratos de dominio de auditoría reutilizables.
from seo_auditor.models import AuditoriaRequest, ConfiguracionCacheAuditoria, ConfiguracionInforme, FlagsIntegracionesAuditoria

# Importa fábrica compartida de adaptadores de servicio.
from seo_auditor.services.adapters_factory import crear_adaptadores_auditoria

# Importa servicio orquestador principal del dominio SEO.
from seo_auditor.services.auditoria_service import AuditoriaService

# Importa catálogo de perfiles contractuales de entregables.
from seo_auditor.services.entregables_service import ENTREGABLES_BASE_AUDITORIA, PERFILES_GENERACION


# Construye request de dominio desde datos validados del formulario web.
def construir_request_desde_formulario(datos: dict[str, Any]) -> AuditoriaRequest:
    """Transforma datos web a `AuditoriaRequest` sin duplicar lógica de negocio."""

    # Carga configuración central para respetar flags y timeouts existentes.
    configuracion = cargar_configuracion()

    # Define periodo desde el formulario en formato ISO compatible.
    periodo_desde = datos["fecha_inicio"].isoformat()

    # Define periodo hasta el formulario en formato ISO compatible.
    periodo_hasta = datos["fecha_fin"].isoformat()

    # Propaga periodo a integraciones autenticadas igual que la CLI.
    configuracion.gsc_date_from = periodo_desde

    # Propaga fecha final para GSC y GA4 manteniendo consistencia.
    configuracion.gsc_date_to = periodo_hasta

    # Propaga fecha inicial para el flujo de Analytics.
    configuracion.ga_date_from = periodo_desde

    # Propaga fecha final para el flujo de Analytics.
    configuracion.ga_date_to = periodo_hasta

    # Resuelve perfil documental según selección de generar todo.
    perfil_generacion = "todo" if datos.get("generar_todo") else "auditoria-seo-completa"

    # Construye flags de integración usando configuración y formulario.
    integraciones = FlagsIntegracionesAuditoria(
        usar_search_console=bool(configuracion.gsc_enabled),
        usar_analytics=bool(configuracion.ga_enabled),
        usar_pagespeed=bool(configuracion.pagespeed_api_key),
        usar_ia=bool(datos.get("usar_ia")),
        usar_ga4_premium=perfil_generacion == "todo",
    )

    # Define configuración de caché para ejecución web.
    cache = ConfiguracionCacheAuditoria(
        ruta_cache="./salidas/.cache",
        ttl_segundos=int(datos.get("cache_ttl") or 0),
        invalidar_antes_de_ejecutar=False,
    )

    # Define configuración de informe para exportación documental.
    informe = ConfiguracionInforme(
        perfil_generacion=perfil_generacion,
        modo=str(datos.get("modo_informe") or "completo"),
        carpeta_salida="./salidas",
        entregables_solicitados=list(PERFILES_GENERACION.get(perfil_generacion, ENTREGABLES_BASE_AUDITORIA)),
    )

    # Construye argumentos mínimos legacy requeridos por el servicio.
    argumentos = SimpleNamespace(comparar="periodo-anterior", provincia="", noGSC=False, testia=False, testga=False, testgsc=False)

    # Construye y devuelve el request contractual del núcleo.
    return AuditoriaRequest(
        sitemap=str(datos["sitemap"]).strip(),
        periodo_desde=periodo_desde,
        periodo_hasta=periodo_hasta,
        gestor=str(datos["gestor"]).strip(),
        cliente=str(datos.get("cliente") or "").strip(),
        modelo_ia=configuracion.gemini_model,
        modo_rapido=bool(datos.get("modo_rapido")),
        max_muestras_ia=15,
        pagepsi_url=str(datos.get("pagepsi_url") or "").strip(),
        pagepsi_list_path="",
        max_pagepsi_urls=0,
        pagepsi_timeout=0,
        pagepsi_reintentos=-1,
        integraciones=integraciones,
        cache=cache,
        informe=informe,
        configuracion=configuracion,
        argumentos=argumentos,
    )


# Ejecuta auditoría mediante servicio principal y serializa datos para la vista.
def ejecutar_auditoria_web(request_auditoria: AuditoriaRequest) -> dict[str, Any]:
    """Ejecuta auditoría usando `AuditoriaService` y devuelve resumen serializable."""

    # Crea servicio de auditoría con adaptadores oficiales del núcleo.
    servicio = AuditoriaService(crear_adaptadores_auditoria())

    # Ejecuta el contrato completo para obtener resultado estructurado.
    resultado = servicio.ejecutar_contrato(request_auditoria)

    # Serializa resultado de auditoría para consumo en plantillas.
    auditoria_dict = asdict(resultado.auditoria)

    # Serializa resumen de ejecución para estado y trazabilidad.
    resumen_dict = asdict(resultado.resumen_ejecucion)

    # Serializa entregables para listar descargas disponibles.
    entregables_dict = asdict(resultado.entregables)

    # Devuelve paquete serializado para persistencia y render.
    return {
        "auditoria": auditoria_dict,
        "resumen": resumen_dict,
        "entregables": entregables_dict,
    }
