# Importa herramientas para construir dataframe de prueba.
import pandas as pd

# Importa helper de indexación a validar.
from seo_auditor.indexacion import _extraer_disallow_por_user_agent


# Verifica que Disallow se filtre correctamente por User-agent objetivo.
def test_extraer_disallow_por_user_agent_filtra_bloques() -> None:
    """Comprueba que solo se extraigan reglas Disallow del bloque aplicable."""

    # Construye dataframe simulando robots con dos bloques de agentes.
    robots_df = pd.DataFrame(
        [
            {"directive": "user-agent", "content": "Googlebot"},
            {"directive": "disallow", "content": "/privado-google/"},
            {"directive": "user-agent", "content": "*"},
            {"directive": "disallow", "content": "/privado-global/"},
        ]
    )

    # Extrae patrones para wildcard global.
    patrones = _extraer_disallow_por_user_agent(robots_df, "*")

    # Verifica que se conserve la regla global esperada.
    assert "/privado-global/" in patrones

    # Verifica que no se arrastre regla exclusiva de Googlebot.
    assert "/privado-google/" not in patrones
