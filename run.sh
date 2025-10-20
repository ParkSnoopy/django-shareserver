#!/bin/bash

# Intended to run in script dir
uv run -- granian \
  --interface wsgi \
  --process-name django-shareserver \
  --workers 2 \
  --blocking-threads 8 \
  compactSharing.wsgi:application

#  --uds django-shareserver.sock \
