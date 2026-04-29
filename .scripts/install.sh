#!/bin/env bash

set -x

if [ $EUID -gt 0 ]; then
  echo "Please run as root/sudo"
  exit 1
fi

sudo cp --update=none scripts/django-shareserver.ubuntu.service /etc/systemd/system/django-shareserver.service
sudo systemctl enable --now django-shareserver.service
