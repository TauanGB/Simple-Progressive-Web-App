"""
Configurações de desenvolvimento.
"""
from .base import *  # noqa
import os

# Carrega .env somente em DEV
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

# Em desenvolvimento, DEBUG deve estar habilitado
DEBUG = True

# Obtém o hostname do Codespace se estiver rodando lá
CODESPACE_NAME = os.getenv("CODESPACE_NAME")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

# Adiciona hosts dinâmicos para suportar Codespaces do GitHub
ALLOWED_HOSTS.extend([
    "localhost",
    "127.0.0.1",
])

# Se rodando em Codespace, adiciona o host específico
if CODESPACE_NAME:
    # Formato: {name}.github.dev (para pré-visualização) e {name}-{port}.app.github.dev (para app)
    ALLOWED_HOSTS.extend([
        f"{CODESPACE_NAME}.github.dev",
        f"{CODESPACE_NAME}-8000.app.github.dev",
        # Adiciona também versão sem porta para segurança
        f"{CODESPACE_NAME}.app.github.dev",
    ])
elif os.getenv("HOSTNAME"):
    # Fallback para HOSTNAME se disponível
    hostname = os.getenv("HOSTNAME")
    ALLOWED_HOSTS.append(hostname)
    # Adiciona versão da porta padrão também
    if not hostname.endswith(':8000'):
        ALLOWED_HOSTS.append(f"{hostname}:8000")

# Adiciona também o host do ambiente se definido
if os.getenv("APP_HOST"):
    ALLOWED_HOSTS.append(os.getenv("APP_HOST"))

# Relaxa CORS/CSRF para localhost se não definidos
if not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://*.github.dev",
        "https://*.app.github.dev",
        "https://potential-yodel-qg55vw9xg6jcpgj-8000.app.github.dev",
    ]

if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://*.app.github.dev",
        "https://potential-yodel-qg55vw9xg6jcpgj-8000.app.github.dev",
    ]

# Em desenvolvimento, permite CORS para qualquer origem nos endpoints PWA
CORS_ALLOW_ALL_ORIGINS = True


