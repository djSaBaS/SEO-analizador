# Importa argparse para construir un CLI claro y mantenible.
import argparse

# Importa utilidades de fecha para validar rangos temporales.
from datetime import date, timedelta

# Importa Path para gestionar la carpeta de salida con seguridad.
from pathlib import Path

# Importa tipos para funciones de conectividad reutilizables.
from typing import Any, Callable

# Importa el motor de auditoría SEO.
from seo_auditor.analyzer import auditar_urls

# Importa utilidades de caché local para invalidación opcional.
from seo_auditor.cache import invalidar_cache

# Importa la carga de configuración del entorno.
from seo_auditor.config import cargar_configuracion

# Importa cliente IA y utilidades de prueba.
from seo_auditor.gemini_client import generar_resumen_ia, probar_conexion_ia

# Importa análisis de indexación y rastreo basado en robots/sitemap.
from seo_auditor.indexacion import analizar_indexacion_rastreo, generar_gestion_indexacion_inteligente

# Importa el extractor de URLs desde sitemap.
from seo_auditor.fetcher import extraer_urls_sitemap

# Importa integración opcional con Google Search Console.
from seo_auditor.gsc import cargar_datos_search_console

# Importa integración opcional con Google Analytics 4.
from seo_auditor.ga4 import cargar_datos_analytics

# Importa generador premium de informe dedicado de GA4.
from seo_auditor.ga4_premium import generar_informe_ga4_premium

# Importa modelo de resultado de rendimiento.
from seo_auditor.models import ResultadoRendimiento

# Importa utilidades de PageSpeed.
from seo_auditor.pagespeed import analizar_pagespeed_url, detectar_home

# Importa los exportadores de salida del proyecto.
from seo_auditor.reporters import exportar_excel, exportar_html, exportar_json, exportar_markdown_ia, exportar_pdf, exportar_word

# Importa utilidades de entrada, fecha y estructura de salida.
from seo_auditor.utils import es_url_http_valida, fecha_ejecucion_iso, inferir_cliente_desde_slug, iterar_con_progreso, slug_dominio_desde_url


# Define gestor por defecto para metadatos de informe.
GESTOR_POR_DEFECTO = "Juan Antonio Sánchez Plaza"

# Define identificadores canónicos de entregables SEO.
ENTREGABLE_JSON_TECNICO = "json_tecnico"

# Define identificador canónico de entregable Excel SEO.
ENTREGABLE_EXCEL_SEO = "excel_seo"

# Define identificador canónico de entregable Word SEO.
ENTREGABLE_WORD_SEO = "word_seo"

# Define identificador canónico de entregable PDF SEO.
ENTREGABLE_PDF_SEO = "pdf_seo"

# Define identificador canónico de entregable HTML SEO.
ENTREGABLE_HTML_SEO = "html_seo"

# Define identificador canónico de entregable Markdown IA.
ENTREGABLE_MARKDOWN_IA = "markdown_ia"

# Define identificador canónico de entregable GA4 premium compuesto.
ENTREGABLE_GA4_PREMIUM = "ga4_premium"

# Centraliza la definición de entregables base de auditoría SEO.
ENTREGABLES_BASE_AUDITORIA = [
    ENTREGABLE_JSON_TECNICO,
    ENTREGABLE_EXCEL_SEO,
    ENTREGABLE_WORD_SEO,
    ENTREGABLE_PDF_SEO,
    ENTREGABLE_HTML_SEO,
    ENTREGABLE_MARKDOWN_IA,
]

# Centraliza perfiles de generación para composición de salidas.
PERFILES_GENERACION: dict[str, list[str]] = {
    "auditoria-seo-completa": ENTREGABLES_BASE_AUDITORIA,
    "entrega-cliente": ENTREGABLES_BASE_AUDITORIA,
    "todo": ENTREGABLES_BASE_AUDITORIA + [ENTREGABLE_GA4_PREMIUM],
    "solo-ga4-premium": [ENTREGABLE_GA4_PREMIUM],
}


# Convierte una fecha ISO textual en objeto date con validación clara.
def _parsear_fecha_cli(valor: str, parametro: str) -> date:
    """
    Valida fechas CLI en formato YYYY-MM-DD devolviendo un objeto `date`.
    """

    # Intenta convertir el valor textual a fecha ISO estricta.
    try:
        # Devuelve fecha parseada cuando el formato sea correcto.
        return date.fromisoformat(valor)

    # Propaga error controlado cuando el formato sea inválido.
    except ValueError as exc:
        # Informa con contexto del parámetro inválido.
        raise ValueError(f"{parametro} debe tener formato YYYY-MM-DD.") from exc


# Resuelve el periodo de análisis efectivo para fuentes temporales.
def _resolver_periodo_analisis(argumentos: argparse.Namespace) -> tuple[str, str]:
    """
    Determina y valida `date_from`/`date_to` para toda fuente temporal.
    """

    # Lee valores opcionales recibidos por CLI.
    date_from_cli = argumentos.date_from.strip()

    # Lee fecha fin opcional recibida por CLI.
    date_to_cli = argumentos.date_to.strip()

    # Exige coherencia cuando se pasa solo una de las fechas.
    if bool(date_from_cli) != bool(date_to_cli):
        # Lanza error claro para evitar rangos ambiguos.
        raise ValueError("Debes indicar ambos parámetros: --date-from y --date-to.")

    # Valida y devuelve rango explícito cuando se reciban fechas.
    if date_from_cli:
        # Valida fecha inicial aportada por usuario.
        fecha_desde = _parsear_fecha_cli(date_from_cli, "--date-from")

        # Valida fecha final aportada por usuario.
        fecha_hasta = _parsear_fecha_cli(date_to_cli, "--date-to")

        # Exige rango temporal estricto para coherencia operativa.
        if fecha_desde >= fecha_hasta:
            # Lanza error con reglas del requisito funcional.
            raise ValueError("--date-from debe ser anterior a --date-to.")

        # Devuelve periodo efectivo serializado.
        return fecha_desde.isoformat(), fecha_hasta.isoformat()

    # Usa ayer para evitar datos intradía incompletos en APIs.
    fecha_hasta = date.today() - timedelta(days=1)

    # Calcula ventana inclusiva de 28 días.
    fecha_desde = fecha_hasta - timedelta(days=27)

    # Devuelve periodo efectivo serializado por defecto.
    return fecha_desde.isoformat(), fecha_hasta.isoformat()


# Ejecuta una prueba de conectividad reutilizable para integraciones externas.
def _ejecutar_prueba_conectividad(
    nombre_modo: str,
    nombre_servicio: str,
    configuracion: Any,
    funcion_carga: Callable[[Any], Any],
    mensaje_error_defecto: str,
    pistas_error: list[tuple[list[str], list[str]]],
    formatear_exito: Callable[[Any], str],
) -> int:
    """
    Ejecuta una validación de conectividad e imprime diagnóstico accionable.
    """

    # Informa del servicio externo que se va a validar.
    print(f"[{nombre_modo}] Validando conexión con {nombre_servicio}...")

    # Intenta ejecutar la carga real con la configuración efectiva.
    try:
        # Obtiene dataset o estado de integración.
        datos = funcion_carga(configuracion)

    # Captura errores inesperados de red/auth/dependencias externas.
    except Exception as exc:
        # Informa fallo inesperado con representación detallada.
        print(f"[{nombre_modo}] Error inesperado al conectar con {nombre_servicio}: {exc!r}")

        # Devuelve error al sistema operativo.
        return 1

    # Evalúa si la integración devolvió estado no activo.
    if not datos.activo:
        # Obtiene el texto de error original cuando exista.
        error_original = (datos.error or "").strip()

        # Informa error principal con fallback explícito.
        print(f"[{nombre_modo}] Error: {error_original or mensaje_error_defecto}")

        # Normaliza el error para detectar pistas por patrones.
        error_normalizado = error_original.lower()

        # Recorre mapa de patrones->pistas configurado para el servicio.
        for patrones, pistas in pistas_error:
            # Evalúa si algún patrón aparece en el error.
            if any(patron in error_normalizado for patron in patrones):
                # Emite todas las pistas asociadas al patrón.
                for pista in pistas:
                    # Informa detalle accionable para resolver el fallo.
                    print(f"[{nombre_modo}] Detalle: {pista}")

        # Devuelve error al sistema operativo.
        return 1

    # Informa resultado exitoso con datos de contexto del servicio.
    print(f"[{nombre_modo}] OK. {formatear_exito(datos)}")

    # Devuelve éxito tras la validación.
    return 0


# Carga una lista de URLs desde archivo de texto.
def _cargar_urls_desde_archivo(ruta_archivo: str) -> list[str]:
    """
    Lee URLs desde un archivo plano de forma segura y normalizada.
    """

    # Define objeto Path para validar existencia del archivo.
    ruta = Path(ruta_archivo)

    # Lanza error claro cuando el archivo no exista.
    if not ruta.exists() or not ruta.is_file():
        # Notifica fallo de ruta de entrada.
        raise ValueError(f"No existe el archivo indicado en --pagepsi-list: {ruta_archivo}")

    # Inicializa lista de URLs válidas.
    urls: list[str] = []

    # Recorre líneas del archivo para filtrar URLs válidas.
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        # Elimina espacios alrededor de cada línea.
        candidata = linea.strip()

        # Añade solo URLs válidas para evitar peticiones inválidas.
        if candidata and es_url_http_valida(candidata):
            # Incorpora la URL en orden de aparición.
            urls.append(candidata)

    # Devuelve URLs deduplicadas preservando orden.
    return list(dict.fromkeys(urls))


# Construye lista objetivo para PageSpeed según reglas de negocio.
def _resolver_urls_pagespeed(argumentos: argparse.Namespace, sitemap: str, urls_sitemap: list[str], max_urls: int) -> list[str]:
    """
    Determina URLs a analizar con PageSpeed cumpliendo el comportamiento obligatorio.
    """

    # Prioriza URL única cuando se indique --pagepsi.
    if argumentos.pagepsi:
        # Retorna lista con una única URL validada.
        return [argumentos.pagepsi]

    # Carga lista desde archivo cuando se indique --pagepsi-list.
    if argumentos.pagepsi_list:
        # Obtiene URLs desde archivo y aplica deduplicación.
        urls_archivo = _cargar_urls_desde_archivo(argumentos.pagepsi_list)

        # Aplica fallback a HOME cuando el archivo no contenga URLs válidas.
        if not urls_archivo:
            # Muestra aviso claro para facilitar depuración.
            print("Aviso: --pagepsi-list no contiene URLs válidas. Se analizará la HOME por defecto.")

            # Devuelve la home detectada para no dejar el bloque vacío.
            return [detectar_home(sitemap, urls_sitemap)]

        # Aplica límite de control máximo de URLs.
        return urls_archivo[:max_urls]

    # Aplica comportamiento por defecto: analizar solo home.
    return [detectar_home(sitemap, urls_sitemap)]


# Ejecuta las consultas de PageSpeed para móvil y escritorio por URL.
def _ejecutar_pagespeed(
    urls: list[str],
    api_key: str,
    timeout: int,
    reintentos: int,
    cache_dir: Path | None = None,
    cache_ttl_segundos: int = 0,
) -> list[ResultadoRendimiento]:
    """
    Ejecuta PageSpeed de forma resiliente y sin detener la auditoría global.
    """

    # Inicializa lista consolidada de resultados.
    resultados: list[ResultadoRendimiento] = []

    # Recorre cada URL objetivo de rendimiento.
    for url in iterar_con_progreso(urls, "PageSpeed", "URL"):
        # Informa en consola de la URL bajo análisis.
        print(f"  - PageSpeed URL: {url}")

        # Recorre estrategias obligatorias móvil y escritorio.
        for estrategia in ["mobile", "desktop"]:
            # Informa estrategia activa para trazabilidad.
            print(f"    · estrategia={estrategia} | intento máximo={reintentos + 1}")

            # Ejecuta análisis y acumula resultado con manejo interno de errores.
            resultado = analizar_pagespeed_url(url, api_key, estrategia, timeout, reintentos, cache_dir, cache_ttl_segundos)

            # Informa error controlado por URL/estrategia sin detener flujo.
            if resultado.error:
                # Muestra aviso de error trazable para depuración.
                print(f"    · error={resultado.error}")
            else:
                # Muestra resumen mínimo de score para trazabilidad.
                print(f"    · performance={resultado.performance_score} seo={resultado.seo_score}")

            # Añade resultado a la colección consolidada.
            resultados.append(resultado)

    # Devuelve colección completa de resultados de rendimiento.
    return resultados


# Resuelve nombre de cliente para informe premium desde argumento o sitemap.
def _resolver_cliente_informe_ga4(cliente_cli: str | None, sitemap: str | None) -> str:
    """
    Prioriza nombre explícito de cliente y aplica inferencia robusta desde sitemap.
    """

    # Usa nombre explícito cuando se reciba por CLI.
    if (cliente_cli or "").strip():
        # Devuelve nombre saneado para portada del informe.
        return (cliente_cli or "").strip()

    # Intenta inferir cliente desde sitemap HTTP/HTTPS válido.
    sitemap_normalizado = (sitemap or "").strip()

    # Intenta inferir cliente desde sitemap HTTP/HTTPS válido.
    if sitemap_normalizado and es_url_http_valida(sitemap_normalizado):
        # Deriva cliente desde el slug del dominio.
        return inferir_cliente_desde_slug(slug_dominio_desde_url(sitemap_normalizado))

    # Intenta inferir cliente desde ruta local cuando no sea URL.
    if sitemap_normalizado:
        # Calcula nombre base del archivo o carpeta como fallback.
        nombre = Path(sitemap_normalizado).stem.strip()

        # Devuelve nombre inferido cuando exista valor útil.
        if nombre:
            # Capitaliza para presentación ejecutiva.
            return nombre.replace("_", " ").replace("-", " ").title()

    # Aplica cliente genérico como último recurso.
    return "Cliente GA4"


# Resuelve perfil de generación compuesto desde los argumentos CLI.
def _resolver_perfil_generacion(argumentos: argparse.Namespace) -> str:
    """
    Determina el perfil compuesto de entregables preservando compatibilidad histórica.
    """

    # Prioriza atajo operativo explícito para entrega completa.
    if argumentos.generar_todo:
        # Devuelve perfil compuesto que incluye SEO y GA4 premium opcional.
        return "todo"

    # Devuelve perfil dedicado cuando el modo sea exclusivo de GA4.
    if argumentos.modo == "informe-ga4":
        # Retorna perfil dedicado del informe premium.
        return "solo-ga4-premium"

    # Devuelve perfil compuesto para el nuevo modo de entrega completa.
    if argumentos.modo == "entrega-completa":
        # Retorna perfil que incluye SEO y GA4 premium opcional.
        return "todo"

    # Mantiene comportamiento por defecto para modos históricos SEO.
    return "auditoria-seo-completa"


# Convierte un identificador de entregable en etiqueta legible para logs.
def _etiqueta_entregable(entregable: str) -> str:
    """
    Traduce identificadores internos a etiquetas amigables de consola.
    """

    # Define diccionario de etiquetas de visualización.
    etiquetas = {
        ENTREGABLE_JSON_TECNICO: "JSON técnico",
        ENTREGABLE_EXCEL_SEO: "Excel SEO",
        ENTREGABLE_WORD_SEO: "Word SEO",
        ENTREGABLE_PDF_SEO: "PDF SEO",
        ENTREGABLE_HTML_SEO: "HTML SEO",
        ENTREGABLE_MARKDOWN_IA: "Markdown IA",
        ENTREGABLE_GA4_PREMIUM: "GA4 premium (HTML/PDF/Excel)",
    }

    # Devuelve etiqueta conocida o el identificador en fallback.
    return etiquetas.get(entregable, entregable)


# Construye mapa de funciones exportadoras reutilizable por perfil.
def _crear_exportadores_seo(resultado: Any, carpeta_salida: Path) -> dict[str, Callable[[], Any]]:
    """
    Construye tabla de exportadores SEO sin duplicar lógica documental.
    """

    # Devuelve función de exportación por cada formato SEO.
    return {
        ENTREGABLE_JSON_TECNICO: lambda: exportar_json(resultado, carpeta_salida),
        ENTREGABLE_EXCEL_SEO: lambda: exportar_excel(resultado, carpeta_salida),
        ENTREGABLE_WORD_SEO: lambda: exportar_word(resultado, carpeta_salida),
        ENTREGABLE_PDF_SEO: lambda: exportar_pdf(resultado, carpeta_salida),
        ENTREGABLE_HTML_SEO: lambda: exportar_html(resultado, carpeta_salida),
        ENTREGABLE_MARKDOWN_IA: lambda: exportar_markdown_ia(resultado, carpeta_salida),
    }


# Construye el parser de argumentos del programa.
def crear_parser() -> argparse.ArgumentParser:
    """
    Crea y configura el parser del CLI.
    """

    # Crea el parser principal con descripción orientada al usuario.
    parser = argparse.ArgumentParser(description="Auditor SEO profesional desde sitemap con exportación de informes.")

    # Añade el argumento del sitemap para modo auditoría completa.
    parser.add_argument("--sitemap", required=False, help="URL del sitemap XML a analizar.")

    # Añade el argumento de la carpeta de salida para modo auditoría.
    parser.add_argument("--output", required=False, help="Carpeta raíz donde se guardarán los informes.")

    # Añade el flag para activar el análisis narrativo con IA.
    parser.add_argument("--usar-ia", action="store_true", help="Activa el enriquecimiento del informe con Gemini.")

    # Añade modo de prueba de IA sin generar informes.
    parser.add_argument("--testia", action="store_true", help="Valida conexión y modelo IA con una llamada mínima.")

    # Añade modo de prueba de Google Analytics 4 sin auditoría completa.
    parser.add_argument("--testga", action="store_true", help="Valida conexión con Google Analytics 4 y finaliza.")

    # Añade modo de prueba de Google Search Console sin auditoría completa.
    parser.add_argument("--testgsc", action="store_true", help="Valida conexión con Google Search Console y finaliza.")

    # Añade parámetro opcional para forzar modelo IA en --testia o --usar-ia.
    parser.add_argument("--modelo-ia", default="", help="Sobrescribe temporalmente el modelo de IA para esta ejecución.")

    # Añade selector de modo de prompt para el sistema IA modular.
    parser.add_argument(
        "--modo",
        choices=["completo", "resumen", "quickwins", "gsc", "roadmap", "informe-ga4", "entrega-completa"],
        default="completo",
        help="Selecciona el modo de ejecución/prompt: completo, resumen, quickwins, gsc, roadmap, entrega-completa o informe-ga4.",
    )

    # Añade atajo operativo para generar una entrega completa en una ejecución.
    parser.add_argument(
        "--generar-todo",
        action="store_true",
        help="Atajo de orquestación equivalente a --modo entrega-completa.",
    )

    # Añade parámetro para analizar una URL concreta con PageSpeed.
    parser.add_argument("--pagepsi", default="", help="URL concreta a analizar con PageSpeed Insights.")

    # Añade parámetro opcional para lista de URLs de PageSpeed.
    parser.add_argument("--pagepsi-list", default="", help="Ruta a archivo con URLs para PageSpeed (una por línea).")

    # Añade parámetro para limitar el total de URLs de PageSpeed.
    parser.add_argument("--max-pagepsi-urls", type=int, default=0, help="Límite manual de URLs para PageSpeed (0 usa configuración).")

    # Añade parámetro opcional para timeout de PageSpeed.
    parser.add_argument("--pagepsi-timeout", type=int, default=0, help="Timeout de PageSpeed en segundos (0 usa configuración).")

    # Añade parámetro opcional para reintentos de PageSpeed.
    parser.add_argument("--pagepsi-reintentos", type=int, default=-1, help="Reintentos de PageSpeed (valor negativo usa configuración).")

    # Añade parámetro para definir gestor de la auditoría.
    parser.add_argument("--gestor", default=GESTOR_POR_DEFECTO, help="Nombre del gestor responsable del informe.")

    # Añade parámetro opcional de cliente para portada del informe premium.
    parser.add_argument("--cliente", default="", help="Nombre de cliente para portada de informe premium (opcional).")

    # Añade parámetro para controlar muestras enviadas a IA.
    parser.add_argument("--max-muestras-ia", type=int, default=15, help="Número máximo de muestras agregadas para la IA.")

    # Añade modo rápido para demos y validaciones internas.
    parser.add_argument("--modo-rapido", action="store_true", help="Limita volumen de URLs para una auditoría rápida.")

    # Añade parámetro de TTL para caché local en segundos.
    parser.add_argument("--cache-ttl", type=int, default=0, help="TTL de caché local en segundos (0 usa configuración).")

    # Añade flag para invalidar caché local antes de ejecutar.
    parser.add_argument("--invalidar-cache", action="store_true", help="Elimina la caché local antes de iniciar la auditoría.")

    # Añade flag para omitir explícitamente Search Console en esta ejecución.
    parser.add_argument("--noGSC", action="store_true", help="Desactiva Google Search Console para esta ejecución, aunque esté configurado.")

    # Añade selector de comparación temporal para el informe premium GA4.
    parser.add_argument(
        "--comparar",
        choices=["periodo-anterior", "anio-anterior"],
        default="periodo-anterior",
        help="Comparación temporal para informe GA4: periodo-anterior o anio-anterior.",
    )

    # Añade filtro opcional de provincia para detalle local en informe GA4.
    parser.add_argument("--provincia", default="", help="Provincia objetivo para detalle de ciudades en informe GA4 premium.")

    # Añade fecha inicial global para fuentes temporales.
    parser.add_argument("--date-from", default="", help="Fecha inicial del análisis (YYYY-MM-DD).")

    # Añade fecha final global para fuentes temporales.
    parser.add_argument("--date-to", default="", help="Fecha final del análisis (YYYY-MM-DD).")

    # Devuelve el parser ya configurado.
    return parser


# Ejecuta el flujo principal del programa.
def main() -> int:
    """
    Ejecuta el flujo principal de auditoría SEO.
    """

    # Construye el parser del programa.
    parser = crear_parser()

    # Lee y valida los argumentos de entrada.
    argumentos = parser.parse_args()

    # Carga la configuración desde variables de entorno.
    configuracion = cargar_configuracion()

    # Resuelve el modelo IA efectivo según argumento opcional.
    modelo_ia = argumentos.modelo_ia.strip() or configuracion.gemini_model

    # Resuelve perfil compuesto de generación según argumentos.
    perfil_generacion = _resolver_perfil_generacion(argumentos)

    # Ejecuta modo de prueba IA cuando se solicite explícitamente.
    if argumentos.testia:
        # Informa inicio de validación de IA.
        print("[testia] Validando configuración de IA...")

        # Ejecuta prueba controlada y barata.
        try:
            # Obtiene respuesta de prueba mínima.
            respuesta = probar_conexion_ia(configuracion.gemini_api_key, modelo_ia)

            # Informa resultado exitoso al usuario.
            print(f"[testia] OK. Modelo={modelo_ia}. Respuesta={respuesta}")

            # Finaliza con código de éxito.
            return 0

        # Maneja fallo de forma clara para uso operativo.
        except Exception as exc:
            # Informa error de prueba sin stacktrace extensa.
            print(f"[testia] Error: {exc}")

            # Finaliza con código de error.
            return 1

    # Valida y resuelve periodo efectivo global del análisis.
    try:
        # Obtiene fecha inicial y final para toda fuente temporal.
        periodo_desde, periodo_hasta = _resolver_periodo_analisis(argumentos)
    except ValueError as exc:
        # Informa error de validación de fechas.
        print(f"Error: {exc}")
        # Devuelve error por parámetros inválidos.
        return 1

    # Aplica periodo global a GSC para desacoplar del .env.
    configuracion.gsc_date_from = periodo_desde

    # Aplica periodo global a GSC para desacoplar del .env.
    configuracion.gsc_date_to = periodo_hasta

    # Aplica periodo global a GA4 para desacoplar del .env.
    configuracion.ga_date_from = periodo_desde

    # Aplica periodo global a GA4 para desacoplar del .env.
    configuracion.ga_date_to = periodo_hasta

    # Ejecuta modo de prueba GSC cuando se solicite explícitamente.
    if argumentos.testgsc:
        # Define patrones y pistas accionables específicas de GSC.
        pistas_gsc = [
            (
                ["no existe archivo de credenciales"],
                ["revisa GSC_CREDENTIALS_FILE; la ruta debe apuntar a un JSON de service account accesible."],
            ),
            (
                ["falta gsc_site_url"],
                ["define GSC_SITE_URL (ej.: sc-domain:midominio.com o https://www.midominio.com/)."],
            ),
            (
                ["insufficient", "forbidden", "403"],
                ["la service account no tiene permisos en la propiedad de Search Console."],
            ),
        ]

        # Ejecuta verificación de conectividad GSC reutilizando helper.
        return _ejecutar_prueba_conectividad(
            "testgsc",
            "Google Search Console",
            configuracion,
            cargar_datos_search_console,
            "No se pudo validar la conexión con Search Console.",
            pistas_gsc,
            lambda datos: (
                f"site_url={datos.site_url or configuracion.gsc_site_url} | "
                f"periodo={datos.date_from}..{datos.date_to} | "
                f"filas_paginas={len(datos.paginas)} | "
                f"filas_queries={len(datos.queries)}"
            ),
        )

    # Ejecuta modo de prueba GA4 cuando se solicite explícitamente.
    if argumentos.testga:
        # Define patrones y pistas accionables específicas de GA4.
        pistas_ga4 = [
            (
                ["no existe archivo de credenciales"],
                ["revisa GA_CREDENTIALS_FILE; debe apuntar a un JSON de service account accesible."],
            ),
            (
                ["falta ga_property_id"],
                ["define GA_PROPERTY_ID con el identificador numérico de la propiedad GA4."],
            ),
            (
                ["ga_property_id debe ser numérico"],
                ["elimina prefijos como 'properties/' y deja solo dígitos (ej.: 123456789)."],
            ),
            (
                ["403", "sufficient permissions"],
                [
                    "la service account no tiene acceso a la propiedad GA4.",
                    "añade el email de la service account como Viewer/Analyst en Administrar acceso de la propiedad.",
                ],
            ),
        ]

        # Ejecuta verificación de conectividad GA4 reutilizando helper.
        return _ejecutar_prueba_conectividad(
            "testga",
            "Google Analytics 4",
            configuracion,
            cargar_datos_analytics,
            "No se pudo validar la conexión con Google Analytics 4.",
            pistas_ga4,
            lambda datos: (
                f"property_id={datos.property_id or configuracion.ga_property_id} | "
                f"periodo={datos.date_from}..{datos.date_to} | "
                f"filas_paginas={len(datos.paginas)}"
            ),
        )

    # Ejecuta modo dedicado de informe GA4 premium cuando el perfil sea exclusivo.
    if perfil_generacion == "solo-ga4-premium":
        # Aplica carpeta de salida por defecto para compatibilidad CLI histórica.
        if not argumentos.output:
            # Informa fallback aplicado para trazabilidad.
            print("Aviso: no se indicó --output, se usará ./salidas por compatibilidad.")

            # Asigna ruta por defecto de salida.
            argumentos.output = "./salidas"

        # Resuelve cliente con prioridad explícita y fallback robusto.
        cliente = _resolver_cliente_informe_ga4(argumentos.cliente, argumentos.sitemap)

        # Construye carpeta de salida específica del informe premium.
        carpeta_salida = Path(argumentos.output) / "ga4_premium" / fecha_ejecucion_iso()

        # Informa inicio de construcción del informe dedicado.
        print("[GA4 Premium] Generando informe premium en HTML/PDF/Excel...")

        # Ejecuta generador dedicado con degradación elegante.
        salida_premium = generar_informe_ga4_premium(
            configuracion,
            carpeta_salida,
            cliente,
            argumentos.gestor,
            periodo_desde,
            periodo_hasta,
            argumentos.comparar,
            argumentos.provincia,
        )

        # Verifica si la integración estuvo activa antes de continuar.
        if not salida_premium.get("activo", False):
            # Informa error controlado sin stacktrace.
            print(f"[GA4 Premium] Aviso: {salida_premium.get('error', 'No se pudo generar el informe.')}")

            # Devuelve éxito suave para no romper automatizaciones globales.
            return 0

        # Informa rutas de salida del informe premium.
        print(f"[GA4 Premium] HTML: {salida_premium.get('html')}")
        print(f"[GA4 Premium] PDF: {salida_premium.get('pdf')}")
        print(f"[GA4 Premium] Excel: {salida_premium.get('excel')}")

        # Finaliza modo dedicado correctamente.
        return 0

    # Exige sitemap en modo auditoría normal.
    if not argumentos.sitemap:
        # Informa falta de argumento obligatorio en este modo.
        print("Error: --sitemap es obligatorio salvo en modo --testia, --testga o --testgsc.")

        # Devuelve código de error.
        return 1

    # Aplica carpeta de salida por defecto para compatibilidad CLI histórica.
    if not argumentos.output:
        # Informa fallback aplicado para trazabilidad.
        print("Aviso: no se indicó --output, se usará ./salidas por compatibilidad.")

        # Asigna ruta por defecto de salida.
        argumentos.output = "./salidas"

    # Valida la URL del sitemap antes de cualquier operación externa.
    if not es_url_http_valida(argumentos.sitemap):
        # Informa error de parámetro inválido.
        print("Error: el parámetro --sitemap debe ser una URL HTTP o HTTPS válida.")

        # Devuelve error al sistema.
        return 1

    # Valida que la URL de PageSpeed manual sea válida si existe.
    if argumentos.pagepsi and not es_url_http_valida(argumentos.pagepsi):
        # Informa error de URL inválida.
        print("Error: --pagepsi debe ser una URL HTTP o HTTPS válida.")

        # Devuelve error al sistema.
        return 1

    # Valida la convivencia de parámetros incompatibles.
    if argumentos.pagepsi and argumentos.pagepsi_list:
        # Informa incompatibilidad de parámetros mutuamente excluyentes.
        print("Error: no se puede usar --pagepsi y --pagepsi-list al mismo tiempo.")

        # Devuelve error al sistema.
        return 1

    # Valida que el límite de muestras sea positivo.
    if argumentos.max_muestras_ia <= 0:
        # Informa error de rango del parámetro.
        print("Error: --max-muestras-ia debe ser un entero positivo.")

        # Devuelve error al sistema.
        return 1

    # Valida límite manual de PageSpeed cuando se reciba.
    if argumentos.max_pagepsi_urls < 0:
        # Informa error de rango del parámetro.
        print("Error: --max-pagepsi-urls no puede ser negativo.")

        # Devuelve error al sistema.
        return 1

    # Valida timeout manual de PageSpeed cuando se reciba.
    if argumentos.pagepsi_timeout < 0:
        # Informa error de rango del parámetro.
        print("Error: --pagepsi-timeout no puede ser negativo.")

        # Devuelve error al sistema.
        return 1

    # Valida reintentos manuales de PageSpeed cuando se reciban.
    if argumentos.pagepsi_reintentos < -1:
        # Informa error de rango del parámetro.
        print("Error: --pagepsi-reintentos debe ser -1 o mayor.")

        # Devuelve error al sistema.
        return 1

    # Genera metadatos reales de ejecución.
    fecha = fecha_ejecucion_iso()

    # Deriva slug y nombre de cliente desde el sitemap.
    slug_dominio = slug_dominio_desde_url(argumentos.sitemap)

    # Deriva nombre del cliente desde el slug del dominio.
    cliente = inferir_cliente_desde_slug(slug_dominio)

    # Define carpeta local de caché para llamadas costosas.
    carpeta_cache = Path(argumentos.output) / ".cache"

    # Aplica invalidación explícita de caché cuando el usuario lo solicite.
    if argumentos.invalidar_cache:
        # Elimina entradas cacheadas y muestra trazabilidad.
        total_eliminado = invalidar_cache(carpeta_cache)

        # Informa total eliminado para control operativo.
        print(f"[cache] Entradas eliminadas: {total_eliminado}")

    # Construye la ruta de salida profesional por dominio y fecha.
    carpeta_salida = Path(argumentos.output) / slug_dominio / fecha

    # Obtiene lista de entregables objetivo del perfil resuelto.
    entregables_perfil = PERFILES_GENERACION.get(perfil_generacion, ENTREGABLES_BASE_AUDITORIA)

    # Informa perfil compuesto activo para trazabilidad.
    print(f"[perfil] Ejecutando perfil de generación: {perfil_generacion}")

    # Informa fuentes potenciales según configuración y flags.
    print(
        "[perfil] Fuentes potenciales: "
        f"ia={'on' if argumentos.usar_ia else 'off'} | "
        f"gsc={'off' if argumentos.noGSC else ('on' if configuracion.gsc_enabled else 'off')} | "
        f"ga4={'on' if configuracion.ga_enabled else 'off'} | "
        f"pagespeed={'on' if bool(configuracion.pagespeed_api_key) else 'off'}"
    )

    # Informa entregables planeados para la ejecución.
    print(f"[perfil] Entregables planificados: {', '.join(_etiqueta_entregable(item) for item in entregables_perfil)}")

    # Informa progreso de obtención de URLs.
    print("[1/6] Extrayendo URLs del sitemap...")

    # Extrae las URLs desde el sitemap indicado por el usuario.
    urls = extraer_urls_sitemap(argumentos.sitemap, configuracion.http_timeout, configuracion.max_urls)

    # Aplica modo rápido con muestra reducida para demos o QA.
    if argumentos.modo_rapido:
        # Limita el análisis a una muestra útil y liviana.
        urls = urls[: min(25, len(urls))]

    # Comprueba que el sitemap ha devuelto URLs útiles.
    if not urls:
        # Informa fallo en extracción útil de URLs.
        print("Error: no se han encontrado URLs válidas en el sitemap indicado.")

        # Devuelve error al sistema.
        return 1

    # Informa progreso de auditoría técnica.
    print(f"[2/6] Auditando {len(urls)} URLs...")

    # Ejecuta la auditoría técnica sobre todas las URLs obtenidas.
    resultado = auditar_urls(argumentos.sitemap, urls, configuracion.http_timeout, cliente, fecha, argumentos.gestor)

    # Guarda periodo global en resultado para reporting y futura interfaz web.
    resultado.periodo_date_from = periodo_desde

    # Guarda periodo global en resultado para reporting y futura interfaz web.
    resultado.periodo_date_to = periodo_hasta

    # Ejecuta análisis de indexación y rastreo con robots/sitemap.
    resultado.indexacion_rastreo = analizar_indexacion_rastreo(argumentos.sitemap, urls, configuracion.http_timeout)

    # Calcula clasificación inicial de gestión de indexación sin señales GSC.
    resultado.gestion_indexacion = generar_gestion_indexacion_inteligente(resultado.resultados)

    # Calcula el límite efectivo de URLs para PageSpeed.
    max_pagepsi_urls = argumentos.max_pagepsi_urls if argumentos.max_pagepsi_urls > 0 else configuracion.max_pagepsi_urls

    # Calcula timeout efectivo de PageSpeed.
    pagespeed_timeout = argumentos.pagepsi_timeout if argumentos.pagepsi_timeout > 0 else configuracion.pagespeed_timeout

    # Calcula reintentos efectivos de PageSpeed.
    pagespeed_reintentos = argumentos.pagepsi_reintentos if argumentos.pagepsi_reintentos >= 0 else configuracion.pagespeed_reintentos

    # Calcula TTL efectivo de caché local.
    cache_ttl = argumentos.cache_ttl if argumentos.cache_ttl > 0 else configuracion.cache_ttl_segundos

    # Ejecuta PageSpeed si existe clave API configurada.
    if configuracion.pagespeed_api_key:
        # Informa progreso del bloque de rendimiento.
        print("[3/6] Ejecutando PageSpeed Insights...")

        # Resuelve URLs objetivo según reglas funcionales.
        urls_pagespeed = _resolver_urls_pagespeed(argumentos, argumentos.sitemap, urls, max_pagepsi_urls)

        # Ejecuta análisis de rendimiento y guarda resultados.
        resultado.rendimiento = _ejecutar_pagespeed(
            urls_pagespeed,
            configuracion.pagespeed_api_key,
            pagespeed_timeout,
            pagespeed_reintentos,
            carpeta_cache / "pagespeed",
            cache_ttl,
        )

        # Inicializa estado de ejecución de PageSpeed por URL.
        estado_pagespeed: dict[str, dict[str, str]] = {}

        # Recorre resultados para construir estado estructurado.
        for item in resultado.rendimiento:
            # Garantiza nodo por URL dentro del estado.
            estado_pagespeed.setdefault(item.url, {})

            # Registra estado por estrategia según éxito o error.
            estado_pagespeed[item.url][item.estrategia] = item.error or "ok"

        # Guarda estado de PageSpeed dentro del resultado final.
        resultado.pagespeed_estado = estado_pagespeed

        # Recalcula score de rendimiento desde resultados disponibles.
        scores_rendimiento_validos = [item.performance_score for item in resultado.rendimiento if isinstance(item.performance_score, (int, float))]

        # Actualiza score de rendimiento cuando existan métricas válidas.
        if scores_rendimiento_validos:
            # Guarda promedio real de rendimiento.
            resultado.score_rendimiento = round(sum(scores_rendimiento_validos) / len(scores_rendimiento_validos), 1)

            # Recalcula SEO score global con componente de rendimiento real.
            resultado.seo_score_global = round(
                (float(resultado.score_tecnico or 0.0) * 0.4)
                + (float(resultado.score_contenido or 0.0) * 0.4)
                + (float(resultado.score_rendimiento or 0.0) * 0.2),
                1,
            )

        # Determina si existe al menos un resultado con métricas válidas.
        hay_metricas_validas = any(
            (
                item.performance_score is not None
                or item.accessibility_score is not None
                or item.best_practices_score is not None
                or item.seo_score is not None
                or item.lcp is not None
                or item.cls is not None
                or item.inp is not None
                or item.fcp is not None
                or item.tbt is not None
                or item.speed_index is not None
            )
            and not item.error
            for item in resultado.rendimiento
        )

        # Añade fuente activa solo cuando hay métricas útiles reales.
        if hay_metricas_validas:
            # Registra fuente activa válida para reporting/IA.
            resultado.fuentes_activas.append("pagespeed")
        else:
            # Registra fuente fallida cuando no hay métricas válidas.
            resultado.fuentes_fallidas.append("pagespeed")
            # Informa causa general en consola de forma profesional.
            print("Aviso: no se pudieron obtener métricas válidas de PageSpeed en esta ejecución.")

    # Informa cuando no haya clave de PageSpeed y se omita bloque.
    else:
        # Muestra mensaje informativo para evitar confusión.
        print("[3/6] PageSpeed omitido: no existe PAGESPEED_API_KEY en entorno.")

    # Evalúa si GSC debe desactivarse por argumento puntual.
    if argumentos.noGSC:
        # Informa desactivación manual para trazabilidad.
        print("[3.5/6] Search Console omitido por argumento --noGSC.")

    # Ejecuta Search Console solo cuando esté habilitado y no se fuerce omisión.
    elif configuracion.gsc_enabled:
        # Informa progreso de integración opcional autenticada.
        print("[3.5/6] Consultando Google Search Console...")

        # Intenta consultar Search Console sin romper flujo global.
        try:
            # Carga dataset opcional de Search Console.
            datos_search_console = cargar_datos_search_console(configuracion)

            # Guarda datos GSC en resultado consolidado.
            resultado.search_console = datos_search_console

            # Recalcula gestión de indexación con señales GSC cuando existan datos.
            resultado.gestion_indexacion = generar_gestion_indexacion_inteligente(resultado.resultados, datos_search_console.paginas)

            # Registra fuente activa cuando existan datos válidos.
            if datos_search_console.activo and (datos_search_console.paginas or datos_search_console.queries):
                # Añade Search Console a fuentes activas.
                resultado.fuentes_activas.append("search_console")
            else:
                # Añade Search Console a fuentes fallidas para trazabilidad.
                resultado.fuentes_fallidas.append("search_console")

                # Informa motivo de degradación elegante en consola.
                print(f"Aviso: Search Console no devolvió datos útiles: {datos_search_console.error or 'sin filas en el rango.'}")

        # Captura error inesperado de integración sin detener auditoría.
        except Exception as exc:
            # Registra fuente fallida por error de integración.
            resultado.fuentes_fallidas.append("search_console")

            # Informa fallo no bloqueante con contexto.
            print(f"Aviso: fallo no bloqueante en Search Console: {exc}")

    # Ejecuta Analytics solo cuando esté habilitado en configuración.
    if configuracion.ga_enabled:
        # Informa progreso de integración opcional autenticada.
        print("[3.7/6] Consultando Google Analytics 4...")

        # Intenta consultar Analytics sin romper flujo global.
        try:
            # Carga dataset opcional de Analytics.
            datos_analytics = cargar_datos_analytics(configuracion)

            # Guarda datos Analytics en resultado consolidado.
            resultado.analytics = datos_analytics

            # Registra fuente activa cuando existan datos válidos.
            if datos_analytics.activo and datos_analytics.paginas:
                # Añade Analytics a fuentes activas.
                resultado.fuentes_activas.append("analytics")
            else:
                # Añade Analytics a fuentes fallidas para trazabilidad.
                resultado.fuentes_fallidas.append("analytics")

                # Informa motivo de degradación elegante en consola.
                print(f"Aviso: Analytics no devolvió datos útiles: {datos_analytics.error or 'sin filas en el rango.'}")

        # Captura error inesperado de integración sin detener auditoría.
        except Exception as exc:
            # Registra fuente fallida por error de integración.
            resultado.fuentes_fallidas.append("analytics")

            # Informa fallo no bloqueante con contexto.
            print(f"Aviso: fallo no bloqueante en Analytics: {exc}")

    # Genera el resumen con IA solo si el usuario lo solicita.
    if argumentos.usar_ia:
        # Informa progreso de IA.
        print("[4/6] Generando resumen ejecutivo con IA...")

        # Ejecuta generación IA con degradación elegante ante errores.
        try:
            # Genera resumen narrativo optimizado en tokens.
            resultado.resumen_ia = generar_resumen_ia(
                resultado,
                configuracion.gemini_api_key,
                modelo_ia,
                argumentos.max_muestras_ia,
                argumentos.modo if argumentos.modo in {"completo", "resumen", "quickwins", "gsc", "roadmap"} else "completo",
                carpeta_cache / "ia",
                cache_ttl,
            )

            # Añade fuente IA si la generación se completa.
            resultado.fuentes_activas.append("ia")

        # Captura fallos de IA sin detener generación técnica.
        except Exception as exc:
            # Registra mensaje de degradación controlada.
            resultado.resumen_ia = f"No se pudo generar el informe con IA: {exc}"

    # Informa progreso de exportación de entregables.
    print("[5/6] Exportando entregables profesionales...")

    # Inicializa colección de entregables generados correctamente.
    archivos_generados: list[str] = []

    # Inicializa colección de entregables omitidos por perfil o disponibilidad.
    archivos_omitidos: list[str] = []

    # Inicializa colección de errores no fatales por exportador.
    errores_no_fatales: list[str] = []

    # Construye mapa de exportadores SEO para evitar condicionales dispersos.
    exportadores_seo = _crear_exportadores_seo(resultado, carpeta_salida)

    # Recorre entregables planificados según perfil compuesto.
    for entregable in iterar_con_progreso(entregables_perfil, "Exportación", "archivo"):
        # Resuelve etiqueta legible del entregable actual.
        etiqueta = _etiqueta_entregable(entregable)

        # Ejecuta exportación SEO estándar cuando exista función registrada.
        if entregable in exportadores_seo:
            # Intenta generar cada exportador de forma aislada.
            try:
                # Ejecuta la función concreta de exportación.
                exportadores_seo[entregable]()
                # Añade entregable a la colección de éxito.
                archivos_generados.append(etiqueta)
                # Informa tarea completada en consola.
                print(f"  - Exportado: {etiqueta}")
            # Captura fallo aislado sin romper toda la entrega.
            except Exception as exc:
                # Registra error no fatal para resumen final.
                errores_no_fatales.append(f"{etiqueta}: {exc}")
                # Informa degradación elegante sin cortar ejecución.
                print(f"  - Aviso: no se pudo exportar {etiqueta}: {exc}")
            # Continúa con el siguiente entregable del perfil.
            continue

        # Ejecuta integración opcional de informe GA4 premium compuesto.
        if entregable == ENTREGABLE_GA4_PREMIUM:
            # Omite GA4 premium cuando la fuente GA4 no esté habilitada.
            if not configuracion.ga_enabled:
                # Registra omisión por incompatibilidad de fuente.
                archivos_omitidos.append(f"{etiqueta} (GA4 no habilitado)")
                # Informa omisión controlada en consola.
                print("  - Omitido: GA4 premium porque GA4 no está habilitado.")
                # Continúa con el siguiente entregable del perfil.
                continue

            # Resuelve cliente premium reutilizando helper existente.
            cliente_premium = _resolver_cliente_informe_ga4(argumentos.cliente, argumentos.sitemap)

            # Construye carpeta específica del informe premium.
            carpeta_salida_premium = Path(argumentos.output) / "ga4_premium" / fecha

            # Intenta generar bloque premium sin romper auditoría base.
            try:
                # Ejecuta generación premium con el mismo periodo temporal.
                salida_premium = generar_informe_ga4_premium(
                    configuracion,
                    carpeta_salida_premium,
                    cliente_premium,
                    argumentos.gestor,
                    periodo_desde,
                    periodo_hasta,
                    argumentos.comparar,
                    argumentos.provincia,
                )

                # Registra omisión cuando el generador no esté activo.
                if not salida_premium.get("activo", False):
                    # Registra motivo controlado de omisión premium.
                    motivo = salida_premium.get("error", "sin detalle de error")
                    archivos_omitidos.append(f"{etiqueta} ({motivo})")
                    # Informa degradación premium no bloqueante.
                    print(f"  - Omitido: {etiqueta}. Motivo: {motivo}")
                else:
                    # Registra entregable premium como generado.
                    archivos_generados.append(etiqueta)
                    # Informa salidas premium individuales para trazabilidad.
                    print(f"  - Exportado: {etiqueta}")
                    print(f"    · HTML: {salida_premium.get('html')}")
                    print(f"    · PDF: {salida_premium.get('pdf')}")
                    print(f"    · Excel: {salida_premium.get('excel')}")
            # Captura fallos premium como error no fatal aislado.
            except Exception as exc:
                # Registra incidencia premium como no fatal.
                errores_no_fatales.append(f"{etiqueta}: {exc}")
                # Informa error no bloqueante del entregable premium.
                print(f"  - Aviso: no se pudo exportar {etiqueta}: {exc}")
            # Continúa con el siguiente entregable del perfil.
            continue

        # Registra entregable desconocido como omitido para diagnóstico.
        archivos_omitidos.append(f"{etiqueta} (no reconocido)")
        # Informa inconsistencia de perfil para trazabilidad.
        print(f"  - Omitido: {etiqueta} no está registrado en el orquestador.")

    # Finaliza con mensaje de éxito y ruta final.
    print(f"[6/6] Auditoría completada. Ruta base de salida: {carpeta_salida.resolve()}")
    # Informa entregables realmente generados.
    print(f"[6/6] Generados: {archivos_generados or ['ninguno']}")
    # Informa entregables omitidos cuando aplique.
    print(f"[6/6] Omitidos: {archivos_omitidos or ['ninguno']}")
    # Informa errores no fatales para revisión operativa.
    print(f"[6/6] Errores no fatales: {errores_no_fatales or ['ninguno']}")

    # Calcula score y promedios de rendimiento para resumen de cierre.
    total_incidencias = sum(len(item.hallazgos) for item in resultado.resultados)

    # Calcula score global replicando fórmula de reporters.
    score_estimado = round(max(5.0, min(100.0, 100.0 - (total_incidencias / max(1, resultado.total_urls * 2)) * 10.0)), 1)

    # Calcula score móvil promedio si existe.
    scores_mobile = [item.performance_score for item in resultado.rendimiento if item.estrategia == "mobile" and isinstance(item.performance_score, (int, float))]

    # Calcula score escritorio promedio si existe.
    scores_desktop = [item.performance_score for item in resultado.rendimiento if item.estrategia == "desktop" and isinstance(item.performance_score, (int, float))]

    # Emite resumen corto en consola para UX de cierre.
    print(
        "Resumen: "
        f"urls={resultado.total_urls} | "
        f"periodo={periodo_desde}..{periodo_hasta} | "
        f"incidencias={total_incidencias} | "
        f"score={score_estimado} | "
        f"mobile={round(sum(scores_mobile) / len(scores_mobile), 1) if scores_mobile else 'N/D'} | "
        f"desktop={round(sum(scores_desktop) / len(scores_desktop), 1) if scores_desktop else 'N/D'} | "
        f"salida={carpeta_salida.resolve()}"
    )

    # Devuelve éxito al sistema operativo.
    return 0
