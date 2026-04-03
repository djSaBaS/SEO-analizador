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

    # Limpia ejecuciones huérfanas al arrancar la app web.
    def ready(self) -> None:
        """Marca en error ejecuciones `en_proceso` que quedaron bloqueadas."""

        # Importa timezone para mensajes de trazabilidad temporal.
        from django.utils import timezone

        # Importa modelo local dentro de ready para evitar side effects de import.
        from seo_auditor.web.apps.auditorias.models import EjecucionAuditoria

        # Define mensaje de recuperación para ejecuciones huérfanas por reinicio.
        mensaje_recuperacion = (
            "Ejecución interrumpida por reinicio del servidor "
            f"({timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')})."
        )

        # Marca en error cualquier ejecución que siguió en proceso tras un reinicio.
        EjecucionAuditoria.objects.filter(estado=EjecucionAuditoria.ESTADO_EN_PROCESO).update(
            estado=EjecucionAuditoria.ESTADO_ERROR,
            mensaje_error=mensaje_recuperacion,
        )
