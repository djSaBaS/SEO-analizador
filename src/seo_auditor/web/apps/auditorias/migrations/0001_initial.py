"""Migración inicial para persistencia mínima de ejecuciones web."""

# Importa motor de migraciones de Django.
from django.db import migrations, models


# Define operación inicial de creación del modelo de ejecución.
class Migration(migrations.Migration):
    """Crea el modelo de trazabilidad ligera para auditorías web."""

    # Declara que no depende de migraciones previas en esta app.
    initial = True

    # Define dependencias de esta migración.
    dependencies = []

    # Define operaciones de esquema a aplicar en base de datos.
    operations = [
        migrations.CreateModel(
            name="EjecucionAuditoria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                ("cliente", models.CharField(blank=True, max_length=200)),
                ("sitemap", models.URLField(max_length=600)),
                ("gestor", models.CharField(max_length=200)),
                ("fecha_inicio", models.DateField()),
                ("fecha_fin", models.DateField()),
                ("estado", models.CharField(choices=[("pendiente", "Pendiente"), ("en_proceso", "En proceso"), ("finalizada", "Finalizada"), ("error", "Error")], default="pendiente", max_length=20)),
                ("ruta_salida", models.CharField(blank=True, max_length=800)),
                ("fuentes_activas", models.JSONField(blank=True, default=list)),
                ("fuentes_fallidas", models.JSONField(blank=True, default=list)),
                ("resumen_resultado", models.JSONField(blank=True, default=dict)),
                ("entregables", models.JSONField(blank=True, default=list)),
                ("mensaje_error", models.TextField(blank=True)),
            ],
            options={"verbose_name": "Ejecución de auditoría", "verbose_name_plural": "Ejecuciones de auditoría", "ordering": ["-fecha_creacion"]},
        ),
    ]
