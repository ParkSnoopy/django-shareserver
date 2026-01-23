from django.db import models
from django.conf import settings

from datetime import datetime, timedelta, timezone
from pathlib import Path
from os import path, remove

from localutils.private_level import PrivateLevel

# Create your models here.


def expire_time_maker(lifetime_in_hour=settings.MY_DEFAULT_FILE_LIFETIME_IN_HOUR):
    # If `<project>.settings.py` have set `TIME_ZONE` and `USE_TZ`,
    # then all time will display as Local Time, even if this returns
    # UTC time as result. 
    return datetime.now(tz=timezone.utc) + timedelta(hours=lifetime_in_hour)


class SecretFileManager(models.Manager):

    def remove_not_exist(self):
        # Remove case: No Physical File, Exist Object
        for obj in self.all():
            if not obj.filepath.exists():
                obj.delete()

        # Remove case: No Object, Exist Physical File
        exist_obj_filenames = [ obj.filepath for obj in self.all() ]
        for filepath in ( settings.MEDIA_ROOT / settings.LIGHTFILE_SAVE_DIR ).iterdir():
            if filepath not in exist_obj_filenames:
                remove(filepath)

    def remove_expired(self):
        # Remove case: Expired Object
        for obj in self.all():
            if datetime.now(timezone.utc) > obj.expire_at:
                remove(obj.filepath)
                obj.delete()

class PasswordlessSecretFileManager(models.Manager):
    def get_queryset(self):
        # Return MUST be <public, passwordless> objects
        return super().get_queryset().filter(private_level=PrivateLevel.Public).filter(password__isnull=True)


class SecretFile(models.Model):

    private_level = models.IntegerField(blank=False, null=False, default=PrivateLevel.Public)
    password = models.CharField(blank=False, null=True, max_length=1024) # string salted+hashed by 'custom_hasher()'
    title = models.CharField(blank=False, null=False, max_length=128)
    content = models.FileField(blank=False, null=False, upload_to=settings.LIGHTFILE_SAVE_DIR)
    posted_by = models.CharField(blank=False, null=False, max_length=128)
    expire_at = models.DateTimeField(blank=False, null=False, default=expire_time_maker)


    objects = SecretFileManager()
    passwordless_objects = PasswordlessSecretFileManager()


    def __repr__(self):
        return f"File No. {self.pk} ( {self.title} )"
    __str__ = __repr__

    @property
    def filesize(self):
        return self.content.size

    @property
    def filepath(self):
        return settings.MEDIA_ROOT / self.content.name

    @property
    def filename(self):
        return self.filepath.name
