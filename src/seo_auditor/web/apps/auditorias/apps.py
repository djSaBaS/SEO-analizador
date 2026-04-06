"""Definición de la aplicación de auditorías web."""

# Importa la clase base de configuración de aplicaciones Django.
from django.apps import AppConfig
from threading import Lock


# Protege la recuperación para ejecutarla como máximo una vez por proceso.
_RECUPERACION_HUERFANAS_LOCK = Lock()


# Registra metadatos de la aplicación de auditorías internas.
class AuditoriasConfig(AppConfig):
    """Configura la app de auditorías para la capa web interna."""

    # Define el tipo de campo primario automático por defecto.
    default_auto_field = "django.db.models.BigAutoField"

    # Define la ruta Python completa de la aplicación.
    name = "seo_auditor.web.apps.auditorias"

    # Define un nombre legible para panel administrativo.
    verbose_name = "Auditorías SEO internas"

    # Evita re-ejecutar la recuperación en nuevas conexiones del proceso.
    _recuperacion_huerfanas_ejecutada = False

    # Registra la recuperación de ejecuciones huérfanas al arrancar la app.
    def ready(self) -> None:
        """Registra una recuperación diferida de ejecuciones huérfanas."""

        # Importa señal al abrir conexión para evitar consultas en inicialización.
        from django.db.backends.signals import connection_created

        # Registra receptor con identificador estable para evitar duplicados.
        connection_created.connect(
            self._marcar_ejecuciones_huerfanas,
            dispatch_uid="auditorias.recuperar_en_proceso_en_conexion",
        )

    # Marca ejecuciones pendientes cuando ya existe conexión operativa.
    def _marcar_ejecuciones_huerfanas(self, sender, connection, **kwargs) -> None:
        """Marca como error ejecuciones en proceso tras reconectar el servicio."""

        # Evita tocar conexiones no principales (p. ej., réplicas o pruebas especiales).
        if connection.alias != "default":
            return

        # Garantiza que la recuperación solo se ejecute una única vez por proceso.
        with _RECUPERACION_HUERFANAS_LOCK:
            if self._recuperacion_huerfanas_ejecutada:
                return
            self._recuperacion_huerfanas_ejecutada = True

        # Importa excepciones SQL para control defensivo de esquema incompleto.
        from django.db import OperationalError, ProgrammingError
        from django.utils import timezone

        # Importa modelo local al momento de uso para minimizar efectos colaterales.
        from seo_auditor.web.apps.auditorias.models import EjecucionAuditoria

        # Obtiene el nombre físico de tabla asociado al modelo.
        tabla_ejecuciones = EjecucionAuditoria._meta.db_table

        try:
            # Salta actualización si aún no se ejecutaron migraciones en la base actual.
            if tabla_ejecuciones not in connection.introspection.table_names():
                return

            # Define mensaje de recuperación para ejecuciones huérfanas por reinicio.
            mensaje_recuperacion = (
                "Ejecución interrumpida por reinicio del servidor "
                f"({timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')})."
            )

            # Marca en error cualquier ejecución que siguió en proceso tras un reinicio.
            EjecucionAuditoria.objects.filter(
                estado=EjecucionAuditoria.ESTADO_EN_PROCESO
            ).update(
                estado=EjecucionAuditoria.ESTADO_ERROR,
                mensaje_error=mensaje_recuperacion,
            )
        except (OperationalError, ProgrammingError):
            # Ignora entornos sin migraciones aplicadas (por ejemplo, CI en `check`).
            return
