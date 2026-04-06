"""Configuración WSGI para servir la capa web interna."""

# Importa utilidades de entorno para inyectar settings.
import os

# Importa constructor de aplicación WSGI de Django.
from django.core.wsgi import get_wsgi_application

# Define módulo de configuración Django para esta capa web.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seo_auditor.web.config.settings")

# Expone la aplicación WSGI lista para servidor.
application = get_wsgi_application()
