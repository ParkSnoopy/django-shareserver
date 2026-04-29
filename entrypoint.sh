#!/bin/env bash

PROJECT_ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

set -x


# Environ Init
cd $PROJECT_ROOT/compactSharing
cp .env.example .env
sed -i 's/^URLs =.*/URLs = 0.0.0.0/' .env
sed -i "s/^DJANGO_SECRET_KEY =.*/DJANGO_SECRET_KEY = $(cat \/dev\/urandom | LC_ALL=C tr -dc a-zA-Z0-9 | head -c 128)/" .env
cd $PROJECT_ROOT

# Django Init
/usr/local/bin/uv sync
/usr/local/bin/uv run -- python manage.py collectstatic --noinput
/usr/local/bin/uv run -- python manage.py migrate

  DJANGO_SUPERUSER_USERNAME=admin \
  DJANGO_SUPERUSER_PASSWORD=adminpassword \
/usr/local/bin/uv run -- python manage.py createsuperuser --noinput

# Run with `granian`
/usr/local/bin/uv run -- granian \
  --interface wsgi \
  --process-name django-shareserver \
  --workers 1 \
  --blocking-threads 4 \
  --host 0.0.0.0 \
  --port 8000\
  compactSharing.wsgi:application
