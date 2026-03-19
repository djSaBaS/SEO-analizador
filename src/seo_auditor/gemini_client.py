# Importa serialización JSON para enviar contexto técnico a la IA.
import json

# Importa la utilidad oficial para convertir dataclasses en estructuras serializables.
from dataclasses import asdict

# Importa el cliente oficial actual de Google Gemini.
from google import genai

# Importa el modelo de resultado global para tipado claro.
from seo_auditor.models import ResultadoAuditoria


# Convierte el resultado técnico en un resumen narrativo con IA.
def generar_resumen_ia(resultado: ResultadoAuditoria, api_key: str, model_name: str) -> str:
    """
    Genera un resumen ejecutivo SEO usando Google AI Studio.

    Parameters
    ----------
    resultado : ResultadoAuditoria
        Resultado técnico consolidado de la auditoría.
    api_key : str
        Clave de API de Gemini.
    model_name : str
        Nombre del modelo configurado.

    Returns
    -------
    str
        Informe textual enriquecido por IA.

    Raises
    ------
    ValueError
        Si no se proporciona clave de API.
    """

    # Valida que exista una clave de API antes de llamar al servicio externo.
    if not api_key:
        # Corta el flujo con un mensaje claro y no ambiguo.
        raise ValueError("No se ha configurado GEMINI_API_KEY.")

    # Instancia el cliente del SDK con la clave indicada por entorno.
    cliente = genai.Client(api_key=api_key)

    # Construye una vista resumida y segura de los datos técnicos.
    datos = {
        # Incluye el sitemap auditado para contextualizar el dominio o proyecto.
        "sitemap": resultado.sitemap,
        # Incluye el número total de URLs analizadas.
        "total_urls": resultado.total_urls,
        # Incluye un subconjunto estructurado de resultados con foco ejecutivo.
        "resultados": [
            {
                # Expone la URL auditada como unidad de análisis.
                "url": item.url,
                # Expone el tipo lógico inferido de la URL.
                "tipo": item.tipo,
                # Expone el código HTTP observado.
                "estado_http": item.estado_http,
                # Expone si hubo redirección.
                "redirecciona": item.redirecciona,
                # Expone la URL final resuelta.
                "url_final": item.url_final,
                # Expone el título para interpretación editorial.
                "title": item.title,
                # Expone el H1 para interpretación semántica.
                "h1": item.h1,
                # Expone la meta description para interpretación de CTR.
                "meta_description": item.meta_description,
                # Expone la canonical declarada si existe.
                "canonical": item.canonical,
                # Expone si la página marca noindex.
                "noindex": item.noindex,
                # Expone los hallazgos convertidos de forma compatible con dataclasses con slots.
                "hallazgos": [asdict(hallazgo) for hallazgo in item.hallazgos],
                # Expone el error controlado de la URL si existe.
                "error": item.error,
            }
            # Recorre cada resultado auditado para incluirlo en el contexto de la IA.
            for item in resultado.resultados
        ],
    }

    # Define un prompt acotado, útil y orientado a negocio.
    prompt = (
        "Actúa como una agencia SEO senior especializada en auditoría técnica y estratégica. "
        "A partir de estos datos técnicos en JSON, redacta en español un informe profesional con: "
        "1) resumen ejecutivo, 2) problemas críticos, 3) quick wins, 4) acciones técnicas, "
        "5) acciones de contenido, 6) roadmap en corto, medio y largo plazo. "
        "No inventes datos que no estén soportados por el JSON. "
        "Datos de la auditoría:\n"
        + json.dumps(datos, ensure_ascii=False)
    )

    # Ejecuta la generación del contenido con el modelo indicado.
    respuesta = cliente.models.generate_content(
        # Indica el modelo configurado en el entorno.
        model=model_name,
        # Envía el prompt como contenido de entrada.
        contents=prompt,
    )

    # Devuelve el texto generado de forma segura y directa.
    return getattr(respuesta, "text", "") or "No se pudo generar el informe con IA."