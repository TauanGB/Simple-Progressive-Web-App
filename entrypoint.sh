#!/usr/bin/env sh
set -e

# Migra e coleta estáticos
python foco_especializado/manage.py migrate --noinput
python foco_especializado/manage.py collectstatic --noinput

# Sobe gunicorn na porta do Railway
exec gunicorn foco_especializado.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 3 \
  --timeout 120


