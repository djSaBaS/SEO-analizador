"""Modelos mínimos de persistencia para trazabilidad de ejecuciones web."""

# Importa modelos de Django para persistencia relacional mínima.
from django.db import models


# Define el registro mínimo de una ejecución de auditoría web.
class EjecucionAuditoria(models.Model):
    """Persistencia ligera de auditorías ejecutadas desde la interfaz web."""

    # Declara estado pendiente para ejecuciones recién creadas.
    ESTADO_PENDIENTE = "pendiente"

    # Declara estado en ejecución para procesos en curso.
    ESTADO_EN_PROCESO = "en_proceso"

    # Declara estado final exitoso para ejecución completada.
    ESTADO_FINALIZADA = "finalizada"

    # Declara estado de error controlado cuando la ejecución falla.
    ESTADO_ERROR = "error"

    # Define catálogo de estados permitidos para la ejecución.
    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_EN_PROCESO, "En proceso"),
        (ESTADO_FINALIZADA, "Finalizada"),
        (ESTADO_ERROR, "Error"),
    ]

    # Guarda la fecha de creación del registro en base de datos.
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Guarda la fecha de última actualización del estado.
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Guarda el cliente operativo asociado a la auditoría.
    cliente = models.CharField(max_length=200, blank=True)

    # Guarda el sitemap objetivo auditado desde el formulario.
    sitemap = models.URLField(max_length=600)

    # Guarda el gestor responsable de la ejecución.
    gestor = models.CharField(max_length=200)

    # Guarda fecha inicial del periodo analizado.
    fecha_inicio = models.DateField()

    # Guarda fecha final del periodo analizado.
    fecha_fin = models.DateField()

    # Guarda estado actual de la ejecución.
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)

    # Guarda ruta de salida principal cuando la ejecución finaliza.
    ruta_salida = models.CharField(max_length=800, blank=True)

    # Guarda fuentes activas detectadas por la auditoría.
    fuentes_activas = models.JSONField(default=list, blank=True)

    # Guarda fuentes fallidas detectadas por la auditoría.
    fuentes_fallidas = models.JSONField(default=list, blank=True)

    # Guarda resumen serializado útil para mostrar resultados en web.
    resumen_resultado = models.JSONField(default=dict, blank=True)

    # Guarda lista de entregables serializados para descargas.
    entregables = models.JSONField(default=list, blank=True)

    # Guarda mensaje de error no fatal o fatal de la ejecución.
    mensaje_error = models.TextField(blank=True)

    # Define metadatos administrativos del modelo persistente.
    class Meta:
        """Configura orden y nombres legibles del modelo."""

        # Fuerza orden descendente por creación para panel y dashboard.
        ordering = ["-fecha_creacion"]

        # Define nombre singular visible en admin.
        verbose_name = "Ejecución de auditoría"

        # Define nombre plural visible en admin.
        verbose_name_plural = "Ejecuciones de auditoría"

    # Devuelve texto legible del registro para debugging y admin.
    def __str__(self) -> str:
        """Representación de la ejecución para trazabilidad operativa."""

        # Devuelve identificador corto con cliente y estado.
        return f"Ejecución #{self.pk} - {self.cliente or 'Sin cliente'} ({self.estado})"
