import os
from pathlib import Path
from .base import *  # noqa

# Carregar .env apenas em desenvolvimento
BASE_DIR = Path(__file__).resolve().parents[2]

try:
    # Prefer django-environ se instalado, senão fallback para python-dotenv
    import environ  # type: ignore

    env = environ.Env()
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        environ.Env.read_env(str(env_file))
except Exception:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(dotenv_path=BASE_DIR / ".env")
    except Exception:
        pass

DEBUG = True

# Em dev, usar wildcard e localhost se não definido
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

# CORS/CSRF em dev: se não definidos, liberar localhost
if not CORS_ALLOWED_ORIGINS:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

# Em dev, manter STATIC_ROOT padrão do base (BASE_DIR/staticfiles)
# MEDIA_ROOT idem


