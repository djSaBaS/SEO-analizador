"""Servicio de validación de coherencia entre dominio auditado y fuentes externas."""

# Importa utilidades de URL para normalizar hosts de forma robusta.
from urllib.parse import urlparse


# Limpia esquema, prefijos y puerto para comparar dominios de forma consistente.
def normalizar_host_fuente(valor: str) -> str:
    """Normaliza hosts de sitemap, GSC, GA4 y URLs de PageSpeed para comparación."""

    # Limpia espacios laterales de la entrada original.
    texto = (valor or "").strip().lower()

    # Devuelve cadena vacía cuando no hay entrada utilizable.
    if not texto:
        return ""

    # Elimina prefijo sc-domain usado por Search Console.
    if texto.startswith("sc-domain:"):
        # Conserva solo el dominio bruto definido en la propiedad.
        texto = texto.split(":", 1)[1].strip()

    # Añade esquema temporal para parsear entradas sin protocolo.
    if not texto.startswith(("http://", "https://")):
        # Construye URL temporal para extraer host correctamente.
        texto = f"https://{texto}"

    # Parsea la URL normalizada para extraer netloc/hostname.
    parseada = urlparse(texto)

    # Obtiene hostname sin credenciales ni puerto.
    host = (parseada.hostname or "").strip().lower()

    # Elimina prefijo www para comparar dominio raíz.
    if host.startswith("www."):
        # Conserva host canónico sin subdominio público.
        host = host[4:]

    # Devuelve host normalizado para validaciones cruzadas.
    return host


# Compara dos valores de fuente determinando si comparten dominio normalizado.
def dominios_coherentes(valor_auditado: str, valor_fuente: str) -> bool:
    """Indica si dos referencias de dominio corresponden al mismo host normalizado."""

    # Normaliza dominio auditado para comparación estable.
    host_auditado = normalizar_host_fuente(valor_auditado)

    # Normaliza dominio de fuente externa para comparación estable.
    host_fuente = normalizar_host_fuente(valor_fuente)

    # Devuelve falso cuando alguna de las entradas no es comparable.
    if not host_auditado or not host_fuente:
        return False

    # Permite igualdad exacta de host tras normalización.
    if host_auditado == host_fuente:
        return True

    # Permite subdominio del dominio auditado como caso compatible.
    if host_fuente.endswith(f".{host_auditado}"):
        return True

    # Permite que dominio auditado sea subdominio del host fuente.
    if host_auditado.endswith(f".{host_fuente}"):
        return True

    # Devuelve falso cuando no se encuentra relación coherente.
    return False


# Genera etiqueta de incompatibilidad estandarizada para trazabilidad en ejecución.
def construir_detalle_incompatibilidad(nombre_fuente: str, valor_fuente: str, valor_auditado: str) -> str:
    """Construye mensaje legible para registrar exclusiones por dominio."""

    # Normaliza host auditado para mostrar en el detalle.
    host_auditado = normalizar_host_fuente(valor_auditado)

    # Normaliza host fuente para mostrar en el detalle.
    host_fuente = normalizar_host_fuente(valor_fuente)

    # Devuelve texto de incompatibilidad homogéneo para logs y web.
    return (
        f"{nombre_fuente} incompatible: dominio fuente '{host_fuente or valor_fuente}' "
        f"no coincide con dominio auditado '{host_auditado or valor_auditado}'."
    )
