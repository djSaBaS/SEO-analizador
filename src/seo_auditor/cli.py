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

# Importa utilidades de entrada, fecha y estructura de salida.
from seo_auditor.utils import es_url_http_valida, fecha_ejecucion_iso, inferir_cliente_desde_slug, slug_dominio_desde_url


# Define gestor por defecto para metadatos de informe.
GESTOR_POR_DEFECTO = "Juan Antonio Sánchez Plaza"


# Construye el parser de argumentos del programa.
def crear_parser() -> argparse.ArgumentParser:
    """
    Crea y configura el parser del CLI.
    """

    # Crea el parser principal con descripción orientada al usuario.
    parser = argparse.ArgumentParser(description="Auditor SEO profesional desde sitemap con exportación de informes.")

    # Añade el argumento obligatorio del sitemap.
    parser.add_argument("--sitemap", required=True, help="URL del sitemap XML a analizar.")

    # Añade el argumento obligatorio de la carpeta de salida.
    parser.add_argument("--output", required=True, help="Carpeta raíz donde se guardarán los informes.")

    # Añade el flag para activar el análisis narrativo con IA.
    parser.add_argument("--usar-ia", action="store_true", help="Activa el enriquecimiento del informe con Gemini.")

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

    # Valida la URL del sitemap antes de cualquier operación externa.
    if not es_url_http_valida(argumentos.sitemap):
        print("Error: el parámetro --sitemap debe ser una URL HTTP o HTTPS válida.")
        return 1

    # Valida que el límite de muestras sea positivo.
    if argumentos.max_muestras_ia <= 0:
        print("Error: --max-muestras-ia debe ser un entero positivo.")
        return 1

    # Carga la configuración desde variables de entorno.
    configuracion = cargar_configuracion()

    # Genera metadatos reales de ejecución.
    fecha = fecha_ejecucion_iso()

    # Deriva slug y nombre de cliente desde el sitemap.
    slug_dominio = slug_dominio_desde_url(argumentos.sitemap)
    cliente = inferir_cliente_desde_slug(slug_dominio)

    # Construye la ruta de salida profesional por dominio y fecha.
    carpeta_salida = Path(argumentos.output) / slug_dominio / fecha

    # Informa progreso de obtención de URLs.
    print("[1/5] Extrayendo URLs del sitemap...")

    # Extrae las URLs desde el sitemap indicado por el usuario.
    urls = extraer_urls_sitemap(argumentos.sitemap, configuracion.http_timeout, configuracion.max_urls)

    # Comprueba que el sitemap ha devuelto URLs útiles.
    if not urls:
        print("Error: no se han encontrado URLs válidas en el sitemap indicado.")
        return 1

    # Informa progreso de auditoría técnica.
    print(f"[2/5] Auditando {len(urls)} URLs...")

    # Ejecuta la auditoría técnica sobre todas las URLs obtenidas.
    resultado = auditar_urls(argumentos.sitemap, urls, configuracion.http_timeout, cliente, fecha, argumentos.gestor)

    # Genera el resumen con IA solo si el usuario lo solicita.
    if argumentos.usar_ia:
        print("[3/5] Generando resumen ejecutivo con IA...")
        try:
            resultado.resumen_ia = generar_resumen_ia(
                resultado,
                configuracion.gemini_api_key,
                configuracion.gemini_model,
                argumentos.max_muestras_ia,
            )
        except Exception as exc:
            resultado.resumen_ia = f"No se pudo generar el informe con IA: {exc}"

    # Informa progreso de exportación de entregables.
    print("[4/5] Exportando entregables profesionales...")

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
    print(f"[5/5] Auditoría completada. Archivos generados en: {carpeta_salida.resolve()}")

    # Devuelve éxito al sistema operativo.
    return 0
