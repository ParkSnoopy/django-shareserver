from django.shortcuts import redirect
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

from localutils.private_level import PrivateLevel
from lightfileshare.enums import DetailStatus

from pathlib import Path

FPH = settings.MY_FILE_PERMISSION_HANDLER

# Create your views here.


def static(request, appname:str, filetype:str, filename:str):
    filepath = settings.STATIC_ROOT / appname / filetype / filename

    if _is_subdir(settings.STATIC_ROOT, filepath):
        return FileResponse(
            open( filepath , 'rb' )
        )
    return HttpResponse(status=403)

def media_by_file_permission(request, filename:str):
    if not FPH.check_permission(request, filename, _debug=settings.DEBUG):
        # goto Index page if no file permission
        return redirect(f'/?fail={DetailStatus.FailNoPermission}')

    rootpath = settings.MEDIA_ROOT / settings.LIGHTFILE_SAVE_DIR
    filepath = rootpath / filename

    if _is_subdir(rootpath, filepath):
        return FileResponse(
            open( filepath , 'rb' )
        )
    return HttpResponse(status=403)

def _is_subdir(root, sub):
    return root in sub.parents
