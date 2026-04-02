"""Rutas raíz de la capa web interna."""

# Importa función include para componer rutas por aplicación.
from django.urls import include, path


# Declara el conjunto principal de rutas de la web interna.
urlpatterns = [
    # Monta las rutas funcionales de auditorías en la raíz.
    path("", include("seo_auditor.web.apps.auditorias.urls")),
]
