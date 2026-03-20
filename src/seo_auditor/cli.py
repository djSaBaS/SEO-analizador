# Importa argparse para construir un CLI claro y mantenible.
import argparse

# Importa Path para gestionar la carpeta de salida con seguridad.
from pathlib import Path

# Importa el motor de auditoría SEO.
from seo_auditor.analyzer import auditar_urls

# Importa la carga de configuración del entorno.
from seo_auditor.config import cargar_configuracion

# Importa cliente IA y utilidades de prueba.
from seo_auditor.gemini_client import generar_resumen_ia, probar_conexion_ia

# Importa el extractor de URLs desde sitemap.
from seo_auditor.fetcher import extraer_urls_sitemap

# Importa modelo de resultado de rendimiento.
from seo_auditor.models import ResultadoRendimiento

# Importa utilidades de PageSpeed.
from seo_auditor.pagespeed import analizar_pagespeed_url, detectar_home

# Importa los exportadores de salida del proyecto.
from seo_auditor.reporters import exportar_excel, exportar_json, exportar_markdown_ia, exportar_pdf, exportar_word

# Importa utilidades de entrada, fecha y estructura de salida.
from seo_auditor.utils import es_url_http_valida, fecha_ejecucion_iso, inferir_cliente_desde_slug, slug_dominio_desde_url


# Define gestor por defecto para metadatos de informe.
GESTOR_POR_DEFECTO = "Juan Antonio Sánchez Plaza"


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

        # Aplica límite de control máximo de URLs.
        return urls_archivo[:max_urls]

    # Aplica comportamiento por defecto: analizar solo home.
    return [detectar_home(sitemap, urls_sitemap)]


# Ejecuta las consultas de PageSpeed para móvil y escritorio por URL.
def _ejecutar_pagespeed(urls: list[str], api_key: str, timeout: int) -> list[ResultadoRendimiento]:
    """
    Ejecuta PageSpeed de forma resiliente y sin detener la auditoría global.
    """

    # Inicializa lista consolidada de resultados.
    resultados: list[ResultadoRendimiento] = []

    # Recorre cada URL objetivo de rendimiento.
    for url in urls:
        # Informa en consola de la URL bajo análisis.
        print(f"  - PageSpeed URL: {url}")

        # Recorre estrategias obligatorias móvil y escritorio.
        for estrategia in ["mobile", "desktop"]:
            # Informa estrategia activa para trazabilidad.
            print(f"    · estrategia={estrategia}")

            # Ejecuta análisis y acumula resultado con manejo interno de errores.
            resultados.append(analizar_pagespeed_url(url, api_key, estrategia, timeout))

    # Devuelve colección completa de resultados de rendimiento.
    return resultados


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

    # Añade parámetro opcional para forzar modelo IA en --testia o --usar-ia.
    parser.add_argument("--modelo-ia", default="", help="Sobrescribe temporalmente el modelo de IA para esta ejecución.")

    # Añade parámetro para analizar una URL concreta con PageSpeed.
    parser.add_argument("--pagepsi", default="", help="URL concreta a analizar con PageSpeed Insights.")

    # Añade parámetro opcional para lista de URLs de PageSpeed.
    parser.add_argument("--pagepsi-list", default="", help="Ruta a archivo con URLs para PageSpeed (una por línea).")

    # Añade parámetro para limitar el total de URLs de PageSpeed.
    parser.add_argument("--max-pagepsi-urls", type=int, default=0, help="Límite manual de URLs para PageSpeed (0 usa configuración).")

    # Añade parámetro para definir gestor de la auditoría.
    parser.add_argument("--gestor", default=GESTOR_POR_DEFECTO, help="Nombre del gestor responsable del informe.")

    # Añade parámetro para controlar muestras enviadas a IA.
    parser.add_argument("--max-muestras-ia", type=int, default=15, help="Número máximo de muestras agregadas para la IA.")

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

    # Exige sitemap en modo auditoría normal.
    if not argumentos.sitemap:
        # Informa falta de argumento obligatorio en este modo.
        print("Error: --sitemap es obligatorio salvo en modo --testia.")

        # Devuelve código de error.
        return 1

    # Exige output en modo auditoría normal.
    if not argumentos.output:
        # Informa falta de argumento obligatorio en este modo.
        print("Error: --output es obligatorio salvo en modo --testia.")

        # Devuelve código de error.
        return 1

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

    # Genera metadatos reales de ejecución.
    fecha = fecha_ejecucion_iso()

    # Deriva slug y nombre de cliente desde el sitemap.
    slug_dominio = slug_dominio_desde_url(argumentos.sitemap)

    # Deriva nombre del cliente desde el slug del dominio.
    cliente = inferir_cliente_desde_slug(slug_dominio)

    # Construye la ruta de salida profesional por dominio y fecha.
    carpeta_salida = Path(argumentos.output) / slug_dominio / fecha

    # Informa progreso de obtención de URLs.
    print("[1/6] Extrayendo URLs del sitemap...")

    # Extrae las URLs desde el sitemap indicado por el usuario.
    urls = extraer_urls_sitemap(argumentos.sitemap, configuracion.http_timeout, configuracion.max_urls)

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

    # Calcula el límite efectivo de URLs para PageSpeed.
    max_pagepsi_urls = argumentos.max_pagepsi_urls if argumentos.max_pagepsi_urls > 0 else configuracion.max_pagepsi_urls

    # Ejecuta PageSpeed si existe clave API configurada.
    if configuracion.pagespeed_api_key:
        # Informa progreso del bloque de rendimiento.
        print("[3/6] Ejecutando PageSpeed Insights...")

        # Resuelve URLs objetivo según reglas funcionales.
        urls_pagespeed = _resolver_urls_pagespeed(argumentos, argumentos.sitemap, urls, max_pagepsi_urls)

        # Ejecuta análisis de rendimiento y guarda resultados.
        resultado.rendimiento = _ejecutar_pagespeed(urls_pagespeed, configuracion.pagespeed_api_key, configuracion.http_timeout)

        # Añade fuente activa de rendimiento para control editorial.
        resultado.fuentes_activas.append("pagespeed")

    # Informa cuando no haya clave de PageSpeed y se omita bloque.
    else:
        # Muestra mensaje informativo para evitar confusión.
        print("[3/6] PageSpeed omitido: no existe PAGESPEED_API_KEY en entorno.")

    # Genera el resumen con IA solo si el usuario lo solicita.
    if argumentos.usar_ia:
        # Informa progreso de IA.
        print("[4/6] Generando resumen ejecutivo con IA...")

        # Ejecuta generación IA con degradación elegante ante errores.
        try:
            # Genera resumen narrativo optimizado en tokens.
            resultado.resumen_ia = generar_resumen_ia(resultado, configuracion.gemini_api_key, modelo_ia, argumentos.max_muestras_ia)

            # Añade fuente IA si la generación se completa.
            resultado.fuentes_activas.append("ia")

        # Captura fallos de IA sin detener generación técnica.
        except Exception as exc:
            # Registra mensaje de degradación controlada.
            resultado.resumen_ia = f"No se pudo generar el informe con IA: {exc}"

    # Informa progreso de exportación de entregables.
    print("[5/6] Exportando entregables profesionales...")

    # Exporta el resultado técnico a JSON.
    exportar_json(resultado, carpeta_salida)

    # Exporta el detalle técnico a Excel.
    exportar_excel(resultado, carpeta_salida)

    # Exporta el informe ejecutivo a Word.
    exportar_word(resultado, carpeta_salida)

    # Exporta el resumen portable a PDF.
    exportar_pdf(resultado, carpeta_salida)

    # Exporta el informe IA en Markdown cuando exista.
    exportar_markdown_ia(resultado, carpeta_salida)

    # Finaliza con mensaje de éxito y ruta final.
    print(f"[6/6] Auditoría completada. Archivos generados en: {carpeta_salida.resolve()}")

    # Devuelve éxito al sistema operativo.
    return 0
