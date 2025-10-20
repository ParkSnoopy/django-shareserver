#!/bin/bash

# Environ init
pushd compactSharing
cp .env.example .env
sed -i 's/^URLs =.*/URLs = 0.0.0.0/' .env
sed -i "s/^DJANGO_SECRET_KEY =.*/DJANGO_SECRET_KEY = $(cat \/dev\/urandom | LC_ALL=C tr -dc a-zA-Z0-9 | head -c 128)/" .env
popd

# Django init (assume railway)
uv run -- python manage.py collectstatic --noinput
uv run -- python manage.py migrate
uv run -- python manage.py createsuperuser --noinput

# Run with `granian`
uv run -- granian \
  --interface wsgi \
  --process-name django-shareserver \
  --workers 1 \
  --blocking-threads 4 \
  --host 0.0.0.0 \
  --port 8000\
  compactSharing.wsgi:application
