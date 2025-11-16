"""
Configurações de produção.
"""
from .base import *  # noqa

DEBUG = False

# Confiança no proxy do Railway/PL
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


