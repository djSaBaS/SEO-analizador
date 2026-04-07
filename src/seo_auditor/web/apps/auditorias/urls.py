"""Rutas de la aplicación de auditorías web."""

# Importa utilidades de enrutado de Django.
from django.urls import path

# Importa vistas funcionales de la aplicación.
from seo_auditor.web.apps.auditorias import views

# Define namespace para resolver URLs de forma explícita.
app_name = "auditorias"

# Declara rutas de dashboard, creación, detalle y descargas.
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("auditorias/nueva/", views.nueva_auditoria, name="nueva"),
    path("auditorias/<int:ejecucion_id>/", views.detalle_auditoria, name="detalle"),
    path("auditorias/<int:ejecucion_id>/descargar/<int:indice>/", views.descargar_entregable, name="descargar"),
]
