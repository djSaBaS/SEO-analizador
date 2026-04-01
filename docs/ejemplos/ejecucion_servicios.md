# Ejecución por servicios (programática) y por CLI

La **CLI sigue siendo la vía recomendada** para uso operativo diario.

Además, puedes ejecutar el motor desde código Python usando `AuditoriaService` cuando necesites integrarlo en otro sistema (cron, backend, pipeline, etc.).

## 1) Ejecución recomendada (CLI)

```bash
python src/main.py \
  --sitemap https://www.ejemplo.com/sitemap.xml \
  --output ./salidas \
  --usar-ia \
  --modo entrega-completa \
  --date-from 2026-03-01 \
  --date-to 2026-03-31
```

## 2) Ejecución programática (servicio)

```python
from pathlib import Path

from seo_auditor import cli
from seo_auditor.services.auditoria_service import AuditoriaService, construir_request_desde_cli

config = cli.cargar_configuracion()
args = cli.crear_parser().parse_args([
    "--sitemap", "https://www.ejemplo.com/sitemap.xml",
    "--output", "./salidas",
    "--modo", "entrega-completa",
    "--date-from", "2026-03-01",
    "--date-to", "2026-03-31",
])

request = construir_request_desde_cli(
    args,
    config,
    modelo_ia=config.gemini_model,
    periodo_desde="2026-03-01",
    periodo_hasta="2026-03-31",
    perfil_generacion="todo",
)

service = AuditoriaService(cli._crear_adaptadores_temporales())
resultado = service.ejecutar_contrato(request)

print(resultado.resumen_ejecucion.codigo_salida)
print(resultado.entregables.generados)
print(Path(args.output).resolve())
```
