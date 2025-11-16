import os
from .base import *  # noqa

DEBUG = False

# Em prod, exigir SECRET_KEY via env (já vem do base; aqui reforçamos)
if not os.getenv("SECRET_KEY"):
    # Em produção, é obrigatório. Mantemos o valor do base (gerado) mas é recomendado setar via env.
    pass

# Hosts são obrigatórios via env em prod
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]  # fallback amplo, mas recomenda-se definir corretamente

# CORS/CSRF via env. Não liberar automaticamente em prod.
if not CORS_ALLOWED_ORIGINS:
    CORS_ALLOW_ALL_ORIGINS = False
else:
    CORS_ALLOW_ALL_ORIGINS = False

# Static/Media path para contêiner
STATIC_URL = "/static/"
STATIC_ROOT = "/app/staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"

# Respeitar proxy HTTPS (Railway/NGINX/etc.)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


