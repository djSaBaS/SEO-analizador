# Importa el módulo de variables de entorno del sistema.
import os

# Importa la estructura de datos decorada para configuración.
from dataclasses import dataclass

# Importa la carga automática del archivo .env cuando exista.
from dotenv import load_dotenv


# Carga variables del archivo .env de forma transparente y segura.
load_dotenv()


# Define la configuración central del proyecto.
@dataclass(slots=True)
class Configuracion:
    """
    Agrupa los valores de configuración usados por el sistema.

    Parameters
    ----------
    gemini_api_key : str
        Clave de Google AI Studio, opcional.
    gemini_model : str
        Modelo de Gemini configurado.
    http_timeout : int
        Tiempo máximo de espera para peticiones HTTP.
    max_urls : int
        Número máximo de URLs a procesar por ejecución.
    """

    # Guarda la clave de API de Gemini si el usuario la ha configurado.
    gemini_api_key: str

    # Guarda el nombre del modelo a utilizar con Gemini.
    gemini_model: str

    # Guarda el tiempo máximo de espera por petición HTTP.
    http_timeout: int

    # Guarda el límite defensivo de URLs por ejecución.
    max_urls: int


# Carga y valida la configuración desde entorno.
def cargar_configuracion() -> Configuracion:
    """
    Carga la configuración desde variables de entorno.

    Returns
    -------
    Configuracion
        Objeto tipado con la configuración del sistema.

    Raises
    ------
    ValueError
        Si algún valor numérico no es válido.
    """

    # Lee el timeout desde entorno o aplica un valor seguro por defecto.
    timeout_texto = os.getenv("HTTP_TIMEOUT", "15")

    # Lee el límite máximo de URLs desde entorno o aplica un valor prudente.
    max_urls_texto = os.getenv("MAX_URLS", "200")

    # Valida que el timeout sea un entero positivo razonable.
    if not timeout_texto.isdigit() or int(timeout_texto) <= 0:
        # Corta la ejecución con un mensaje controlado y accionable.
        raise ValueError("HTTP_TIMEOUT debe ser un entero positivo.")

    # Valida que el máximo de URLs sea un entero positivo razonable.
    if not max_urls_texto.isdigit() or int(max_urls_texto) <= 0:
        # Corta la ejecución con un mensaje controlado y accionable.
        raise ValueError("MAX_URLS debe ser un entero positivo.")

    # Devuelve la configuración consolidada del proyecto.
    return Configuracion(
        # Carga la clave de Gemini o deja cadena vacía si no existe.
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        # Carga el modelo de Gemini con un valor por defecto estable.
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip(),
        # Convierte el timeout validado a entero.
        http_timeout=int(timeout_texto),
        # Convierte el límite validado a entero.
        max_urls=int(max_urls_texto),
    )
