import os
import secrets
from pathlib import Path

# Base directory (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parents[2]

# Optional: allow PyMySQL as MySQLdb if requested
if os.getenv("USE_PYMYSQL", "").strip() in ("1", "true", "True"):
    try:
        import pymysql  # type: ignore
        pymysql.install_as_MySQLdb()
    except Exception:
        # Falha silenciosa: se não estiver instalado e for necessário,
        # o deploy deverá instalar corretamente. Em dev, normalmente não é usado.
        pass

# Core security and debug flags
DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(50)

# Hosts / CSRF / CORS
def _split_csv_env(key: str) -> list[str]:
    raw = os.getenv(key, "")
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]

ALLOWED_HOSTS = _split_csv_env("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = _split_csv_env("CSRF_TRUSTED_ORIGINS")
CORS_ALLOWED_ORIGINS = _split_csv_env("CORS_ALLOWED_ORIGINS")

DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO").upper()

# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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

# Database: MySQL if MYSQL_HOST is set; otherwise SQLite fallback
if os.getenv("MYSQL_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("MYSQL_DB", ""),
            "USER": os.getenv("MYSQL_USER", ""),
            "PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
            "HOST": os.getenv("MYSQL_HOST", ""),
            "PORT": os.getenv("MYSQL_PORT", "3306"),
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

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static and media
STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles"))
MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login URLs
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# CORS/CSRF defaults (base): apenas aplica se variáveis foram definidas
# Em dev.py, vamos liberar localhost se não houver env.
if CORS_ALLOWED_ORIGINS:
    CORS_ALLOW_ALL_ORIGINS = False

# Logging (console handler, formato curto)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(name)s: %(message)s",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": DJANGO_LOG_LEVEL,
    },
}

# ---------------------------------------------
# Configurações PWA (reaproveitando do projeto)
# ---------------------------------------------
def _get_bool_env(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in ("0", "false", "no", "off")

PWA_ENABLED = _get_bool_env("PWA_ENABLED", True)
PWA_THEME_COLOR = os.getenv("PWA_THEME_COLOR", "#0f172a")
PWA_BACKGROUND_COLOR = os.getenv("PWA_BACKGROUND_COLOR", "#0f172a")
PWA_START_URL = os.getenv("PWA_START_URL", "/?source=pwa")
PWA_SCOPE = os.getenv("PWA_SCOPE", "/")
PWA_PUSH_PUBLIC_KEY = os.getenv("PWA_PUSH_PUBLIC_KEY", "")


