FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=foco_especializado.settings.prod \
    PYTHONPATH=/app/foco_especializado

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY foco_especializado/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Usuário não-root (opcional)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["sh", "./entrypoint.sh"]


