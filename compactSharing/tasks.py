from __future__ import absolute_import, unicode_literals

from celery import shared_task


from lightfileshare.models import SecretFile

import django
django.setup()


@shared_task
def remove_expired():
    SecretFile.objects.remove_not_exist()
    SecretFile.objects.remove_expired()
