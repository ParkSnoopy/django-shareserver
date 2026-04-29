#!/bin/env bash

set -x

# Run with `granian`
/home/ubuntu/.local/bin/uv run -- granian \
  --interface wsgi \
  --process-name django-shareserver \
  --workers 1 \
  --runtime-threads 8 \
  --host 0.0.0.0 \
  --port 8000\
  compactSharing.wsgi:application
