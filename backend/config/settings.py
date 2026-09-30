"""
Configuración del Sistema de Reportes Técnicos.
Pensado para desplegarse como app web dentro de la red interna de la universidad.
Actualizado: 30/09/2026 - Fix PostgreSQL en Railway + ALLOWED_HOSTS auto
"""
import os
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Seguridad básica
# ---------------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-cambiar-en-produccion")
DEBUG = config("DEBUG", default=True, cast=bool)

# ---------------------------------------------------------------------------
# ALLOWED_HOSTS (con auto-detección de dominio de Railway)
# ---------------------------------------------------------------------------
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

# Auto-agregar el dominio público de Railway si existe
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if RAILWAY_DOMAIN and RAILWAY_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_DOMAIN)

# Auto-agregar el dominio estático de Railway si existe
RAILWAY_STATIC_URL = os.environ.get("RAILWAY_STATIC_URL")
if RAILWAY_STATIC_URL:
    from urllib.parse import urlparse
    host = urlparse(f"https://{RAILWAY_STATIC_URL}").hostname
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# Log de dominios permitidos (útil para depurar en Railway)
print(f"[HOST CONFIG] ALLOWED_HOSTS: {ALLOWED_HOSTS}")

# ---------------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    # App propias
    "apps.core",
    "apps.accounts",
    "apps.exports",
    "apps.stats",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Sirve archivos estáticos en producción
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Base de datos
# PostgreSQL en Railway/Supabase, SQLite como fallback local
# ---------------------------------------------------------------------------
import dj_database_url  # noqa: E402

# Leer DATABASE_URL: primero de os.environ (Railway/Docker), luego de .env (local)
DATABASE_URL = os.environ.get("DATABASE_URL") or config("DATABASE_URL", default="")

print(f"[DB CONFIG] DATABASE_URL {'detectada' if DATABASE_URL else 'NO detectada'}")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("[DB CONFIG] Usando PostgreSQL")
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    print("[DB CONFIG] Usando SQLite")

# ---------------------------------------------------------------------------
# Validación de contraseñas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = config("TIME_ZONE", default="America/Bogota")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estáticos y media
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# CORS (el frontend React corre en otro puerto/origen)
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=Csv(),
)

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}

# ---------------------------------------------------------------------------
# Roles del sistema (se crean como Grupos de Django)
# ---------------------------------------------------------------------------
ROL_ADMIN = "Administrador"
ROL_AUDITOR = "Auditor"
ROL_TECNICO = "Tecnico"
ROLES_DISPONIBLES = [ROL_ADMIN, ROL_AUDITOR, ROL_TECNICO]
ROL_POR_DEFECTO = ROL_TECNICO

# ---------------------------------------------------------------------------
# Autenticación: Local
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Autenticación
# Solo autenticación local (usuarios gestionados por el admin en Django)
# ---------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
# ---------------------------------------------------------------------------
# Correo / notificaciones
# ---------------------------------------------------------------------------
EMAIL_HOST = config("EMAIL_HOST", default="")
if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="reportes-ti@universidad.edu")
NOTIFICAR_NUEVOS_REPORTES_A = config("NOTIFICAR_NUEVOS_REPORTES_A", default="", cast=Csv())

# ---------------------------------------------------------------------------
# Configuración de producción
# ---------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=Csv(),
)

# Auto-agregar el dominio de Railway a CSRF_TRUSTED_ORIGINS
if RAILWAY_DOMAIN:
    railway_csrf = f"https://{RAILWAY_DOMAIN}"
    if railway_csrf not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_csrf)
        print(f"[CSRF CONFIG] Agregado: {railway_csrf}")

# Confiar en el proxy de Railway para HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Configuración de seguridad adicional para producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"