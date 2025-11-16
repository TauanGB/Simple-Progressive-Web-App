"""
Configurações base compartilhadas entre ambientes.
"""
from pathlib import Path
import os
import logging

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# ENV - somente leitura direta do ambiente aqui (sem .env)
# Em DEV, o .env será carregado em dev.py
# -----------------------------------------------------------------------------
def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _get_csv_env(name: str, default=None):
    if default is None:
        default = []
    value = os.getenv(name)
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


# -----------------------------------------------------------------------------
# Segurança e depuração
# -----------------------------------------------------------------------------
DEBUG = _get_bool_env("DEBUG", False)
SECRET_KEY = os.getenv("SECRET_KEY") or "dev-insecure-key"
ALLOWED_HOSTS = _get_csv_env("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

# -----------------------------------------------------------------------------
# Aplicações
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceiros
    "corsheaders",
    # Apps do projeto
    "core",
]

# -----------------------------------------------------------------------------
# Middleware
# - WhiteNoise logo após SecurityMiddleware
# - corsheaders antes de CommonMiddleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foco_especializado.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.pwa_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "foco_especializado.wsgi.application"

# -----------------------------------------------------------------------------
# Banco de Dados
# - Se MYSQL_HOST presente -> usa MySQL
# - Caso contrário -> SQLite
# -----------------------------------------------------------------------------
MYSQL_HOST = os.getenv("MYSQL_HOST")
USE_PYMYSQL = _get_bool_env("USE_PYMYSQL", True)

def _get_env_alias(primary: str, aliases: list[str], default: str | None = None) -> str | None:
    value = os.getenv(primary)
    if value:
        return value
    for alias in aliases:
        alias_val = os.getenv(alias)
        if alias_val:
            return alias_val
    return default

# Railway frequentemente usa MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE
MYSQL_HOST = _get_env_alias("MYSQL_HOST", ["MYSQLHOST"])
MYSQL_PORT = _get_env_alias("MYSQL_PORT", ["MYSQLPORT"], "3306")
MYSQL_NAME = _get_env_alias("MYSQL_DB", ["MYSQLDATABASE", "MYSQL_DATABASE", "MYSQL_NAME"])
MYSQL_USER = _get_env_alias("MYSQL_USER", ["MYSQLUSER", "MYSQL_USERNAME"])
MYSQL_PASSWORD = _get_env_alias("MYSQL_PASSWORD", ["MYSQLPASSWORD", "MYSQL_PWD"])

if MYSQL_HOST:
    if USE_PYMYSQL:
        try:
            import pymysql  # type: ignore

            pymysql.install_as_MySQLdb()
        except Exception:
            # Em execução sem a dependência instalada – o container vai cuidar disso
            pass

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": MYSQL_NAME or "",
            "USER": MYSQL_USER or "",
            "PASSWORD": MYSQL_PASSWORD or "",
            "HOST": MYSQL_HOST,
            "PORT": MYSQL_PORT or "3306",
            "CONN_MAX_AGE": 60,
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# -----------------------------------------------------------------------------
# Autenticação e Internacionalização
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Arquivos estáticos e mídia
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = "/app/staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -----------------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# -----------------------------------------------------------------------------
# PWA (mantendo as flags originais para compatibilidade do app atual)
# -----------------------------------------------------------------------------
def _get_bool_env_default_true(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in ("0", "false", "no", "off")


PWA_ENABLED = _get_bool_env_default_true("PWA_ENABLED", True)
PWA_THEME_COLOR = os.getenv("PWA_THEME_COLOR", "#0f172a")
PWA_BACKGROUND_COLOR = os.getenv("PWA_BACKGROUND_COLOR", "#0f172a")
PWA_START_URL = os.getenv("PWA_START_URL", "/?source=pwa")
PWA_SCOPE = os.getenv("PWA_SCOPE", "/")
PWA_PUSH_PUBLIC_KEY = os.getenv("PWA_PUSH_PUBLIC_KEY", "")

# -----------------------------------------------------------------------------
# CORS / CSRF
# -----------------------------------------------------------------------------
from django.utils.functional import lazy

_default_cors = []
_default_csrf = []

CORS_ALLOWED_ORIGINS = _get_csv_env("CORS_ALLOWED_ORIGINS", _default_cors)
CSRF_TRUSTED_ORIGINS = _get_csv_env("CSRF_TRUSTED_ORIGINS", _default_csrf)

# Em DEV (definido em dev.py) adicionamos localhost se vazios

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": DJANGO_LOG_LEVEL,
    },
}


