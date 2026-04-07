"""Formularios de entrada para lanzar auditorías desde web."""

# Importa utilidades de fecha para validación de periodos.
from datetime import date

# Importa formularios de Django para validación robusta.
from django import forms


# Define formulario principal para ejecutar una nueva auditoría.
class NuevaAuditoriaForm(forms.Form):
    """Recoge parámetros de auditoría y valida reglas de negocio básicas."""

    # Define campo sitemap obligatorio con validación de URL.
    sitemap = forms.URLField(label="Sitemap", max_length=600, assume_scheme="https")

    # Define campo opcional de cliente para portada y trazabilidad.
    cliente = forms.CharField(label="Cliente", max_length=200, required=False)

    # Define campo gestor responsable de la auditoría.
    gestor = forms.CharField(label="Gestor", max_length=200, initial="Juan Antonio Sánchez Plaza")

    # Define fecha inicial del periodo analizado.
    fecha_inicio = forms.DateField(label="Fecha inicio", widget=forms.DateInput(attrs={"type": "date"}))

    # Define fecha final del periodo analizado.
    fecha_fin = forms.DateField(label="Fecha fin", widget=forms.DateInput(attrs={"type": "date"}))

    # Define bandera para activar o no la integración de IA.
    usar_ia = forms.BooleanField(label="Usar IA", required=False)

    # Define modo de informe para el prompt narrativo.
    modo_informe = forms.ChoiceField(
        label="Modo informe",
        choices=[
            ("completo", "Completo"),
            ("resumen", "Resumen"),
            ("quickwins", "Quick wins"),
            ("gsc", "GSC"),
            ("roadmap", "Roadmap"),
        ],
        initial="completo",
    )

    # Define campo opcional de URL concreta para PageSpeed.
    pagepsi_url = forms.URLField(
        label="URL concreta PageSpeed",
        required=False,
        max_length=600,
        assume_scheme="https",
    )

    # Define bandera para forzar perfil completo de entregables.
    generar_todo = forms.BooleanField(label="Generar todos los documentos", required=False)

    # Define bandera para limitar volumen y acelerar pruebas internas.
    modo_rapido = forms.BooleanField(label="Modo rápido", required=False)

    # Define TTL opcional de caché para web.
    cache_ttl = forms.IntegerField(label="TTL caché (segundos)", min_value=0, initial=0, required=False)

    # Valida coherencia temporal y restricciones del formulario.
    def clean(self) -> dict:
        """Valida reglas cruzadas de fechas y parámetros incompatibles."""

        # Obtiene datos base aplicando validaciones de campos estándar.
        cleaned_data = super().clean()

        # Recupera fecha de inicio para validación cruzada.
        fecha_inicio = cleaned_data.get("fecha_inicio")

        # Recupera fecha de fin para validación cruzada.
        fecha_fin = cleaned_data.get("fecha_fin")

        # Impide periodos invertidos para mantener consistencia con CLI.
        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            # Registra error de negocio en la fecha final para UX clara.
            self.add_error("fecha_fin", "La fecha fin debe ser posterior a la fecha inicio.")

        # Impide seleccionar fechas futuras para periodos cerrados.
        if fecha_fin and fecha_fin > date.today():
            # Registra error en fecha fin cuando supera la fecha actual.
            self.add_error("fecha_fin", "La fecha fin no puede estar en el futuro.")

        # Devuelve datos limpios para construcción de request interno.
        return cleaned_data
