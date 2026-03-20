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
    """

    # Guarda la clave de API de Gemini si el usuario la ha configurado.
    gemini_api_key: str

    # Guarda el nombre del modelo a utilizar con Gemini.
    gemini_model: str

    # Guarda la clave de API de Google PageSpeed Insights.
    pagespeed_api_key: str

    # Guarda el tiempo máximo de espera por petición HTTP.
    http_timeout: int

    # Guarda el límite defensivo de URLs por ejecución.
    max_urls: int

    # Guarda el límite máximo de URLs para PageSpeed.
    max_pagepsi_urls: int

    # Guarda el timeout de PageSpeed en segundos.
    pagespeed_timeout: int

    # Guarda el número de reintentos de PageSpeed.
    pagespeed_reintentos: int

    # Guarda el TTL por defecto de caché local en segundos.
    cache_ttl_segundos: int


# Carga y valida la configuración desde entorno.
def cargar_configuracion() -> Configuracion:
    """
    Carga la configuración desde variables de entorno.
    """

    # Lee el timeout desde entorno o aplica un valor seguro por defecto.
    timeout_texto = os.getenv("HTTP_TIMEOUT", "15")

    # Lee el límite máximo de URLs desde entorno o aplica un valor prudente.
    max_urls_texto = os.getenv("MAX_URLS", "200")

    # Lee el límite de URLs de PageSpeed o aplica un valor seguro.
    max_pagepsi_texto = os.getenv("MAX_PAGESPEED_URLS", "5")

    # Lee timeout de PageSpeed o aplica valor más robusto.
    pagespeed_timeout_texto = os.getenv("PAGESPEED_TIMEOUT", "45")

    # Lee reintentos de PageSpeed o aplica valor prudente.
    pagespeed_reintentos_texto = os.getenv("PAGESPEED_REINTENTOS", "2")

    # Lee TTL de caché local o aplica valor equilibrado.
    cache_ttl_texto = os.getenv("CACHE_TTL_SEGUNDOS", "21600")

    # Valida que el timeout sea un entero positivo razonable.
    if not timeout_texto.isdigit() or int(timeout_texto) <= 0:
        # Corta la ejecución con un mensaje controlado y accionable.
        raise ValueError("HTTP_TIMEOUT debe ser un entero positivo.")

    # Valida que el máximo de URLs sea un entero positivo razonable.
    if not max_urls_texto.isdigit() or int(max_urls_texto) <= 0:
        # Corta la ejecución con un mensaje controlado y accionable.
        raise ValueError("MAX_URLS debe ser un entero positivo.")

    # Valida que el máximo de URLs de PageSpeed sea positivo.
    if not max_pagepsi_texto.isdigit() or int(max_pagepsi_texto) <= 0:
        # Corta la ejecución con un mensaje claro y accionable.
        raise ValueError("MAX_PAGESPEED_URLS debe ser un entero positivo.")

    # Valida que el timeout de PageSpeed sea positivo.
    if not pagespeed_timeout_texto.isdigit() or int(pagespeed_timeout_texto) <= 0:
        # Corta la ejecución con un mensaje claro y accionable.
        raise ValueError("PAGESPEED_TIMEOUT debe ser un entero positivo.")

    # Valida que el número de reintentos de PageSpeed sea no negativo.
    if not pagespeed_reintentos_texto.isdigit() or int(pagespeed_reintentos_texto) < 0:
        # Corta la ejecución con un mensaje claro y accionable.
        raise ValueError("PAGESPEED_REINTENTOS debe ser un entero igual o mayor que cero.")

    # Valida que TTL de caché sea no negativo.
    if not cache_ttl_texto.isdigit() or int(cache_ttl_texto) < 0:
        # Corta la ejecución con mensaje claro y accionable.
        raise ValueError("CACHE_TTL_SEGUNDOS debe ser un entero igual o mayor que cero.")

    # Devuelve la configuración consolidada del proyecto.
    return Configuracion(
        # Carga la clave de Gemini o deja cadena vacía si no existe.
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        # Carga el modelo de Gemini con un valor por defecto estable.
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip(),
        # Carga la clave de PageSpeed o deja vacío cuando no exista.
        pagespeed_api_key=os.getenv("PAGESPEED_API_KEY", "").strip(),
        # Convierte el timeout validado a entero.
        http_timeout=int(timeout_texto),
        # Convierte el límite validado a entero.
        max_urls=int(max_urls_texto),
        # Convierte el límite de URLs de PageSpeed a entero.
        max_pagepsi_urls=int(max_pagepsi_texto),
        # Convierte timeout de PageSpeed a entero.
        pagespeed_timeout=int(pagespeed_timeout_texto),
        # Convierte reintentos de PageSpeed a entero.
        pagespeed_reintentos=int(pagespeed_reintentos_texto),
        # Convierte TTL de caché a entero.
        cache_ttl_segundos=int(cache_ttl_texto),
    )
