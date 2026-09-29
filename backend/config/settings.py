"""
Configuración del Sistema de Reportes Técnicos.
Pensado para desplegarse como app web dentro de la red interna de la universidad.
"""
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-cambiar-en-produccion")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

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
    "whitenoise.middleware.WhiteNoiseMiddleware",   # ← AÑADIR AQUÍ
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
# fallback a SQLite mientras desarrollas sin conexión
# ---------------------------------------------------------------------------
import dj_database_url

DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL:
    DATABASES = {"default": dj_database_url.config(default=DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = config("TIME_ZONE", default="America/Bogota")
USE_I18N = True
USE_TZ = True

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
    "CORS_ALLOWED_ORIGINS", default="http://localhost:5173,http://127.0.0.1:5173", cast=Csv()
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
# Autenticación: LDAP + Local
# ---------------------------------------------------------------------------
# 1) Definir primero las variables base
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Admin local (superusuario)
]

AUTH_LDAP_SERVER_URI = config("AUTH_LDAP_SERVER_URI", default="")
AD_ROLE_GROUP_MAPPING = {}

# 2) Intentar habilitar LDAP solo si hay URI configurada
LDAP_DISPONIBLE = False

if AUTH_LDAP_SERVER_URI:
    try:
        import ldap
        from django_auth_ldap.config import GroupOfNamesType, LDAPSearch

        LDAP_DISPONIBLE = True
    except ImportError:
        import warnings

        warnings.warn(
            "AUTH_LDAP_SERVER_URI está configurado pero 'python-ldap' no está instalado. "
            "Se usará solo autenticación local.",
            RuntimeWarning,
        )

# 3) Configurar LDAP solo si está disponible
if LDAP_DISPONIBLE:
    AUTH_LDAP_BIND_DN = config("AUTH_LDAP_BIND_DN", default="")
    AUTH_LDAP_BIND_PASSWORD = config("AUTH_LDAP_BIND_PASSWORD", default="")

    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        config("AUTH_LDAP_USER_SEARCH_BASE", default="dc=universidad,dc=edu"),
        ldap.SCOPE_SUBTREE,
        "(sAMAccountName=%(user)s)",
    )
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
        config("AUTH_LDAP_GROUP_SEARCH_BASE", default="dc=universidad,dc=edu"),
        ldap.SCOPE_SUBTREE,
        "(objectClass=group)",
    )
    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")
    AUTH_LDAP_MIRROR_GROUPS = True
    AUTH_LDAP_ALWAYS_UPDATE_USER = True
    AUTH_LDAP_FIND_GROUP_PERMS = True
    AUTH_LDAP_CACHE_TIMEOUT = 3600

    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    }

    AD_ROLE_GROUP_MAPPING = {
        config("AD_GROUP_ADMIN", default="TI-Administradores"): ROL_ADMIN,
        config("AD_GROUP_AUDITOR", default="TI-Auditores"): ROL_AUDITOR,
        config("AD_GROUP_TECNICO", default="TI-Tecnicos"): ROL_TECNICO,
    }

    AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

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

# Permitir CORS desde cualquier subdominio de Railway (para el frontend desplegado)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=Csv(),
)

# Confiar en el proxy de Railway para HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True