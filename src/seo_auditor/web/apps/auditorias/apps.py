"""Definición de la aplicación de auditorías web."""

# Importa la clase base de configuración de aplicaciones Django.
from django.apps import AppConfig


# Registra metadatos de la aplicación de auditorías internas.
class AuditoriasConfig(AppConfig):
    """Configura la app de auditorías para la capa web interna."""

    # Define el tipo de campo primario automático por defecto.
    default_auto_field = "django.db.models.BigAutoField"

    # Define la ruta Python completa de la aplicación.
    name = "seo_auditor.web.apps.auditorias"

    # Define un nombre legible para panel administrativo.
    verbose_name = "Auditorías SEO internas"
