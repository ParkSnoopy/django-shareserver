from django.shortcuts import redirect
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

from localutils.private_level import PrivateLevel
from lightfileshare.enums import DetailStatus
from lightfileshare.models import SecretFile

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
    session_id = request.session.session_key

    # Check existing permission
    if not FPH.check_permission(session_id, filename, _debug=settings.DEBUG):
        _set_passwordless_file_permission(request, filename)

        # IF still_not_accessible THEN fail_no_perm
        if not FPH.check_permission(session_id, filename, _debug=settings.DEBUG):
            # goto Index page if no file permission
            return redirect(f'/?fail={DetailStatus.FailNoPermission}')

    rootpath = settings.MEDIA_ROOT / settings.LIGHTFILE_SAVE_DIR
    filepath = rootpath / filename

    if _is_subdir(rootpath, filepath):
        return FileResponse(
            open( filepath , 'rb' )
        )
    return HttpResponse(status=403)

def _set_passwordless_file_permission(request, filename:str):
    """
    Redundantly mimicking file permission setter in `lightfileshare.views.lightfileshare_details`
      to ensure password-less file shared with URL is directly accessible via `settings.LIGHTFILE_LOAD_URL`
      without being redirected from `/details` which requires a request with the POST method

    Safety: This method blindly allows any object with a given filename to be accessible.
            `SecretFile.passwordless_objects.all()` MUST be objects safe to be accessed by unknowns.
    """

    for file_obj in SecretFile.passwordless_objects.all():
        if filename == file_obj.filename:
            session_id = request.session.session_key
            FPH.set_permission( session_id, filename )

def _is_subdir(root, sub):
    return root in sub.parents
