# Importa el módulo de variables de entorno del sistema.
import os

# Importa la estructura de datos decorada para configuración.
from dataclasses import dataclass

# Importa la carga automática del archivo .env cuando exista.
from dotenv import load_dotenv

# Carga variables del archivo .env de forma transparente y segura.
load_dotenv()


# Convierte valores textuales a booleano de forma robusta.
def _a_booleano(valor: str) -> bool:
    """Normaliza textos de entorno para evaluar banderas booleanas."""

    # Devuelve verdadero para literales habituales de activación.
    return valor.strip().lower() in {"1", "true", "t", "si", "sí", "yes", "y", "on"}


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

    # Guarda si Search Console está habilitado de forma opcional.
    gsc_enabled: bool

    # Guarda la propiedad verificada de Search Console.
    gsc_site_url: str

    # Guarda la ruta al JSON de service account de GSC.
    gsc_credentials_file: str

    # Guarda fecha de inicio del rango GSC.
    gsc_date_from: str

    # Guarda fecha final del rango GSC.
    gsc_date_to: str

    # Guarda el máximo de filas por consulta GSC.
    gsc_row_limit: int

    # Guarda si Analytics está habilitado de forma opcional.
    ga_enabled: bool

    # Guarda el property id de Google Analytics 4.
    ga_property_id: str

    # Guarda la ruta al JSON de service account de GA4.
    ga_credentials_file: str

    # Guarda fecha de inicio del rango GA4.
    ga_date_from: str

    # Guarda fecha final del rango GA4.
    ga_date_to: str

    # Guarda el máximo de filas por consulta GA4.
    ga_row_limit: int

    # Guarda la URL/dominio esperado de GA4 para validación de coherencia.
    ga_site_url: str = ""


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

    # Lee límite de filas de Search Console o aplica valor operativo.
    gsc_row_limit_texto = os.getenv("GSC_ROW_LIMIT", "250")

    # Lee límite de filas de GA4 o aplica valor operativo.
    ga_row_limit_texto = os.getenv("GA_ROW_LIMIT", "1000")

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

    # Valida que el límite de filas GSC sea entero positivo.
    if not gsc_row_limit_texto.isdigit() or int(gsc_row_limit_texto) <= 0:
        # Corta la ejecución con mensaje claro y accionable.
        raise ValueError("GSC_ROW_LIMIT debe ser un entero positivo.")

    # Valida que el límite de filas GA4 sea entero positivo.
    if not ga_row_limit_texto.isdigit() or int(ga_row_limit_texto) <= 0:
        # Corta la ejecución con mensaje claro y accionable.
        raise ValueError("GA_ROW_LIMIT debe ser un entero positivo.")

    # Devuelve la configuración consolidada del proyecto.
    return Configuracion(
        # Carga la clave de Gemini o deja cadena vacía si no existe.
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        # Carga el modelo de Gemini con un valor por defecto estable.
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
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
        # Evalúa bandera booleana de activación GSC.
        gsc_enabled=_a_booleano(os.getenv("GSC_ENABLED", "false")),
        # Carga la propiedad verificada de Search Console.
        gsc_site_url=os.getenv("GSC_SITE_URL", "").strip(),
        # Carga ruta a credenciales de service account.
        gsc_credentials_file=os.getenv("GSC_CREDENTIALS_FILE", "").strip(),
        # Carga fecha inicial de GSC.
        gsc_date_from=os.getenv("GSC_DATE_FROM", "").strip(),
        # Carga fecha final de GSC.
        gsc_date_to=os.getenv("GSC_DATE_TO", "").strip(),
        # Convierte límite de filas de GSC a entero.
        gsc_row_limit=int(gsc_row_limit_texto),
        # Evalúa bandera booleana de activación de GA4.
        ga_enabled=_a_booleano(os.getenv("GA_ENABLED", "false")),
        # Carga property id de GA4.
        ga_property_id=os.getenv("GA_PROPERTY_ID", "").strip(),
        # Carga ruta a credenciales de service account de GA4.
        ga_credentials_file=os.getenv("GA_CREDENTIALS_FILE", "").strip(),
        # Carga fecha inicial de GA4.
        ga_date_from=os.getenv("GA_DATE_FROM", "").strip(),
        # Carga fecha final de GA4.
        ga_date_to=os.getenv("GA_DATE_TO", "").strip(),
        # Convierte límite de filas de GA4 a entero.
        ga_row_limit=int(ga_row_limit_texto),
        # Carga URL/dominio esperado de GA4 para validación de coherencia.
        ga_site_url=os.getenv("GA_SITE_URL", "").strip(),
    )
