#!/bin/bash

# Initialize
touch .env
rm .env
ln -s compactSharing/.env .
uv run -- python manage.py collectstatic --noinput
uv run -- python manage.py migrate

# Run with `granian`
uv run -- granian \
  --interface wsgi \
  --process-name django-shareserver \
  --workers 2 \
  --blocking-threads 8 \
  compactSharing.wsgi:application
