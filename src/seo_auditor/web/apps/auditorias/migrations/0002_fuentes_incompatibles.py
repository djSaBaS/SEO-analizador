"""Añade trazabilidad de fuentes incompatibles por dominio en ejecución web."""

# Importa motor de migraciones de Django.
from django.db import migrations, models


# Define migración incremental para guardar fuentes incompatibles.
class Migration(migrations.Migration):
    """Incorpora campo `fuentes_incompatibles` en `EjecucionAuditoria`."""

    # Define migración previa de la que depende este cambio.
    dependencies = [
        ("auditorias", "0001_initial"),
    ]

    # Declara operaciones de esquema para añadir el nuevo campo JSON.
    operations = [
        migrations.AddField(
            model_name="ejecucionauditoria",
            name="fuentes_incompatibles",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
