# Importa argparse para construir un CLI claro y mantenible.
import argparse

# Importa Path para gestionar la carpeta de salida con seguridad.
from pathlib import Path

# Importa el motor de auditoría SEO.
from seo_auditor.analyzer import auditar_urls

# Importa la carga de configuración del entorno.
from seo_auditor.config import cargar_configuracion

# Importa el cliente opcional de IA.
from seo_auditor.gemini_client import generar_resumen_ia

# Importa el extractor de URLs desde sitemap.
from seo_auditor.fetcher import extraer_urls_sitemap

# Importa los exportadores de salida del proyecto.
from seo_auditor.reporters import exportar_excel, exportar_json, exportar_markdown_ia, exportar_pdf, exportar_word

# Importa la validación de URL de entrada.
from seo_auditor.utils import es_url_http_valida


# Construye el parser de argumentos del programa.
def crear_parser() -> argparse.ArgumentParser:
    """
    Crea y configura el parser del CLI.

    Returns
    -------
    argparse.ArgumentParser
        Parser listo para usarse.
    """

    # Crea el parser principal con descripción orientada al usuario.
    parser = argparse.ArgumentParser(description="Auditor SEO profesional desde sitemap con exportación de informes.")

    # Añade el argumento obligatorio del sitemap.
    parser.add_argument("--sitemap", required=True, help="URL del sitemap XML a analizar.")

    # Añade el argumento obligatorio de la carpeta de salida.
    parser.add_argument("--output", required=True, help="Carpeta donde se guardarán los informes.")

    # Añade el flag para activar el análisis narrativo con IA.
    parser.add_argument("--usar-ia", action="store_true", help="Activa el enriquecimiento del informe con Gemini.")

    # Devuelve el parser ya configurado.
    return parser


# Ejecuta el flujo principal del programa.
def main() -> int:
    """
    Ejecuta el flujo principal de auditoría SEO.

    Returns
    -------
    int
        Código de salida del proceso.
    """

    # Construye el parser del programa.
    parser = crear_parser()

    # Lee y valida los argumentos de entrada.
    argumentos = parser.parse_args()

    # Valida la URL del sitemap antes de cualquier operación externa.
    if not es_url_http_valida(argumentos.sitemap):
        # Informa al usuario de una entrada inválida y termina con error controlado.
        print("Error: el parámetro --sitemap debe ser una URL HTTP o HTTPS válida.")

        # Devuelve código de error estándar.
        return 1

    # Carga la configuración desde variables de entorno.
    configuracion = cargar_configuracion()

    # Convierte la ruta de salida a objeto Path para trabajar de forma segura.
    carpeta_salida = Path(argumentos.output)

    # Extrae las URLs desde el sitemap indicado por el usuario.
    urls = extraer_urls_sitemap(argumentos.sitemap, configuracion.http_timeout, configuracion.max_urls)

    # Comprueba que el sitemap ha devuelto URLs útiles.
    if not urls:
        # Informa de la ausencia de URLs procesables.
        print("Error: no se han encontrado URLs válidas en el sitemap indicado.")

        # Devuelve código de error estándar.
        return 1

    # Ejecuta la auditoría técnica sobre todas las URLs obtenidas.
    resultado = auditar_urls(argumentos.sitemap, urls, configuracion.http_timeout)

    # Genera el resumen con IA solo si el usuario lo solicita.
    if argumentos.usar_ia:
        # Intenta generar el resumen IA sin bloquear la exportación técnica en caso de fallo.
        try:
            # Genera el texto narrativo del informe con Gemini.
            resultado.resumen_ia = generar_resumen_ia(resultado, configuracion.gemini_api_key, configuracion.gemini_model)

        # Captura errores de IA de forma controlada y transparente.
        except Exception as exc:
            # Conserva el error dentro del resumen para que quede trazado en el informe.
            resultado.resumen_ia = f"No se pudo generar el informe con IA: {exc}"

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

    # Informa al usuario de que el proceso ha finalizado correctamente.
    print(f"Auditoría completada. Archivos generados en: {carpeta_salida.resolve()}")

    # Devuelve éxito al sistema operativo.
    return 0
