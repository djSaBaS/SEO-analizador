"""Configuración Django para la primera versión web interna del auditor SEO."""

# Importa utilidades de entorno para leer variables opcionales.
import os

# Importa utilidades criptográficas para clave local efímera en debug.
import secrets

# Importa Path para construir rutas de forma portable.
from pathlib import Path


# Calcula la raíz del repositorio desde el archivo actual.
BASE_DIR = Path(__file__).resolve().parents[4]

# Mantiene modo debug activo para uso local interno.
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"

# Lee la clave secreta desde variables de entorno.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()

# Crea una clave efímera solo cuando debug local está activo.
if not SECRET_KEY and DEBUG:
    # Genera clave temporal para evitar hardcode estático inseguro.
    SECRET_KEY = secrets.token_urlsafe(50)

# Impide arrancar en modo no debug sin clave secreta explícita.
if not SECRET_KEY and not DEBUG:
    # Lanza error claro para forzar configuración segura en despliegues.
    raise RuntimeError("Debes definir DJANGO_SECRET_KEY cuando DJANGO_DEBUG=false.")

# Permite hosts locales habituales para desarrollo interno.
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Registra aplicaciones base de Django necesarias para la web.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "seo_auditor.web.apps.auditorias",
]

# Registra middleware estándar de seguridad y sesión.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Define el archivo raíz de URLs de la capa web.
ROOT_URLCONF = "seo_auditor.web.config.urls"

# Configura el motor de plantillas para render HTML.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "seo_auditor" / "web" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# Define el punto WSGI para servidores compatibles.
WSGI_APPLICATION = "seo_auditor.web.config.wsgi.application"

# Configura base de datos SQLite local para persistencia mínima de ejecuciones.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Activa validadores básicos de contraseña por seguridad por defecto.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Configura idioma principal en español para interfaz y validaciones.
LANGUAGE_CODE = "es-es"

# Configura zona horaria UTC para coherencia con backend actual.
TIME_ZONE = "UTC"

# Mantiene internacionalización activa para textos del framework.
USE_I18N = True

# Mantiene soporte de fechas con zona horaria.
USE_TZ = True

# Define prefijo para servir recursos estáticos.
STATIC_URL = "/static/"

# Define carpeta adicional de estáticos del proyecto web.
STATICFILES_DIRS = [BASE_DIR / "src" / "seo_auditor" / "web" / "static"]

# Define tipo de campo primario por defecto en modelos.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
