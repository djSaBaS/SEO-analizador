# Importa serialización JSON para enviar contexto técnico a la IA.
import json

# Importa contador para resumir hallazgos por frecuencia.
from collections import Counter

# Importa el cliente oficial actual de Google Gemini.
from google import genai

# Importa el modelo de resultado global para tipado claro.
from seo_auditor.models import ResultadoAuditoria


# Construye un resumen optimizado para consumo eficiente de tokens en IA.
def construir_contexto_ia(resultado: ResultadoAuditoria, max_muestras: int) -> dict:
    """
    Crea un contexto agregado y limitado para reducir coste de tokens.
    """

    # Inicializa acumuladores de hallazgos por tipo y severidad.
    contador_problemas: Counter[str] = Counter()

    # Inicializa acumuladores de severidad para visión ejecutiva.
    contador_severidad: Counter[str] = Counter()

    # Inicializa lista con incidencias por URL para ranking.
    urls_con_problemas: list[tuple[str, int]] = []

    # Recorre cada resultado para consolidar métricas globales.
    for item in resultado.resultados:
        # Cuenta el número de hallazgos detectados por URL.
        total_hallazgos_url = len(item.hallazgos)

        # Añade la URL y su volumen de incidencias al ranking.
        urls_con_problemas.append((item.url, total_hallazgos_url))

        # Recorre hallazgos para contar descripciones y severidades.
        for hallazgo in item.hallazgos:
            # Incrementa la frecuencia de cada tipo de problema textual.
            contador_problemas[hallazgo.descripcion] += 1

            # Incrementa la frecuencia de cada severidad clasificada.
            contador_severidad[hallazgo.severidad] += 1

    # Ordena URLs por mayor número de incidencias.
    top_urls = sorted(urls_con_problemas, key=lambda item: item[1], reverse=True)

    # Construye un listado de quick wins basado en bajo esfuerzo y alto/medio impacto.
    quick_wins = []

    # Recorre resultados para detectar incidencias de alto potencial.
    for item in resultado.resultados:
        # Recorre hallazgos de la URL actual.
        for hallazgo in item.hallazgos:
            # Filtra incidencias de esfuerzo bajo y potencial relevante.
            if hallazgo.esfuerzo == "Bajo" and hallazgo.impacto in {"Muy alto", "Alto", "Medio"}:
                # Añade la incidencia al conjunto de quick wins.
                quick_wins.append({"url": item.url, "problema": hallazgo.descripcion, "recomendacion": hallazgo.recomendacion})

    # Devuelve el contexto agregado y limitado para IA.
    return {
        "cliente": resultado.cliente,
        "sitemap": resultado.sitemap,
        "fecha_ejecucion": resultado.fecha_ejecucion,
        "gestor": resultado.gestor,
        "total_urls": resultado.total_urls,
        "total_incidencias": sum(contador_problemas.values()),
        "distribucion_severidad": dict(contador_severidad),
        "top_problemas": [{"problema": problema, "cantidad": cantidad} for problema, cantidad in contador_problemas.most_common(max_muestras)],
        "top_urls_afectadas": [{"url": url, "incidencias": incidencias} for url, incidencias in top_urls[:max_muestras]],
        "muestras_representativas": [
            {
                "url": item.url,
                "estado_http": item.estado_http,
                "redirecciona": item.redirecciona,
                "noindex": item.noindex,
                "hallazgos": [hallazgo.descripcion for hallazgo in item.hallazgos[:3]],
            }
            for item in resultado.resultados[:max_muestras]
        ],
        "quick_wins": quick_wins[:max_muestras],
    }


# Convierte el resultado técnico en un resumen narrativo con IA.
def generar_resumen_ia(resultado: ResultadoAuditoria, api_key: str, model_name: str, max_muestras: int) -> str:
    """
    Genera un resumen ejecutivo SEO usando Google AI Studio.
    """

    # Valida que exista una clave de API antes de llamar al servicio externo.
    if not api_key:
        # Corta el flujo con un mensaje claro y no ambiguo.
        raise ValueError("No se ha configurado GEMINI_API_KEY.")

    # Instancia el cliente del SDK con la clave indicada por entorno.
    cliente = genai.Client(api_key=api_key)

    # Construye el contexto resumido de IA con límite de muestras.
    datos = construir_contexto_ia(resultado, max_muestras)

    # Define un prompt orientado a negocio y sin relleno.
    prompt = (
        "Actúa como consultor SEO senior de agencia. "
        "Redacta un informe en español profesional natural, sin frases vacías ni repeticiones. "
        "Usa solo los datos proporcionados, sin inventar información. "
        "Usa exactamente la fecha de ejecución y el gestor indicados. "
        "Estructura obligatoria: 1) Resumen ejecutivo, 2) Hallazgos críticos, 3) Quick wins, "
        "4) Acciones técnicas, 5) Acciones de contenido, 6) Roadmap priorizado (30/60/90 días). "
        "Separa claramente resumen ejecutivo y anexo técnico. "
        "No uses placeholders ni texto genérico de IA. "
        "Datos de auditoría en JSON:\n"
        + json.dumps(datos, ensure_ascii=False)
    )

    # Ejecuta la generación del contenido con el modelo indicado.
    respuesta = cliente.models.generate_content(model=model_name, contents=prompt)

    # Devuelve el texto generado de forma segura y directa.
    return getattr(respuesta, "text", "") or "No se pudo generar el informe con IA."
