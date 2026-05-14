from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse

from localutils.hasher import custom_hasher, check_password
from localutils.filename_validator import safe_global_filename
from localutils.private_level import PrivateLevel
from localutils.ip_tools import get_ranged_ip

from .models import SecretFile
from .enums import DetailStatus


FPH = settings.MY_FILE_PERMISSION_HANDLER

# Create your views here.


def lightfileshare_home(request):

    SecretFile.objects.remove_not_exist()
    SecretFile.objects.remove_expired()

    private_level = (
        request.user.private_level
        if request.user.is_authenticated
        else PrivateLevel.Public
    )

    return render(
        request,
        "lightfileshare/index.html",
        {
            "objs": SecretFile.objects.filter(
                private_level__lte=private_level
            ).order_by(
                "id"
            ),  # .values('id', 'title', 'posted_by', 'expire_at', 'password', 'content'),
            "alert": DetailStatus.parse(request.GET.get("fail")),
            "info": request.GET.get("info"),
            "status": DetailStatus,
        },
    )


def lightfileshare_details(request):
    if request.method == "POST":
        private_level = (
            request.user.private_level
            if request.user.is_authenticated
            else PrivateLevel.Public
        )

        pk = request.POST.get("id")
        session_id = request.session.session_key

        if pk:
            try:
                secretfile = SecretFile.objects.get(pk=pk)
                filename = secretfile.filename
                # print(f"  POST(get) - {private_level=} CMP {secretfile.private_level=} ; {filename=}")

                if private_level < secretfile.private_level:
                    return redirect(f"/?fail={DetailStatus.FailNoPermission}")

                if secretfile.password:
                    password = request.POST.get("password", "")

                    if check_password(password, secretfile.password):
                        FPH.set_permission(session_id, filename)
                        return redirect(reverse("download", kwargs={"pk": pk}))

                    # print(f"{password=} ; {secretfile.password=} ; check_password={check_password( password, secretfile.password )}")

                    return redirect(f"/?fail={DetailStatus.FailPassword}")

                else:
                    FPH.set_permission(session_id, filename)
                    return redirect(reverse("download", kwargs={"pk": pk}))

            except SecretFile.DoesNotExist:
                return redirect(f"/?fail={DetailStatus.FailNoFileDownload}")

    return redirect(f"/?fail={DetailStatus.FailWrongMethod}")


def lightfileshare_download(request, pk: int):
    try:
        secretfile = SecretFile.objects.get(pk=pk)
    except SecretFile.DoesNotExist:
        return redirect(f"/?fail={DetailStatus.FailNoFileDownload}")

    private_level = (
        request.user.private_level
        if request.user.is_authenticated
        else PrivateLevel.Public
    )

    if private_level < secretfile.private_level:
        return redirect(f"/?fail={DetailStatus.FailNoPermission}")

    session_id = request.session.session_key
    filename = secretfile.filename
    file_url = settings.LIGHTFILE_LOAD_URL + filename

    base_context = {
        "title": secretfile.title,
        "file_url": file_url,
        "filesize": secretfile.filesize,
        "posted_by": secretfile.posted_by,
        "has_password": bool(secretfile.password),
        "status": DetailStatus,
    }

    if request.method == "POST":
        if not secretfile.password:
            FPH.set_permission(session_id, filename)
        else:
            password = request.POST.get("password", "")
            if not check_password(password, secretfile.password):
                return render(
                    request,
                    "lightfileshare/download.html",
                    {
                        **base_context,
                        "needs_password": True,
                        "has_permission": False,
                        "error": DetailStatus.FailPassword,
                    },
                )
            FPH.set_permission(session_id, filename)

        return redirect(reverse("download", kwargs={"pk": pk}))

    # GET: auto-grant permission for passwordless files
    has_permission = FPH.check_permission(session_id, filename)
    if not secretfile.password:
        FPH.set_permission(session_id, filename)
        has_permission = True

    return render(
        request,
        "lightfileshare/download.html",
        {
            **base_context,
            "needs_password": bool(secretfile.password) and not has_permission,
            "has_permission": has_permission,
            "error": DetailStatus.Init,
        },
    )


# ** IMPORTANT **
# `create` page has its own response handler with AJAX.
# This page is designed to recieve a JSON response.
# If any other response (e.g. `return redirect('/')`) is sent,
#   this page considers full HTML page as JSON file and
#   fails to parse it into JSON Object.
#
# Also, to show `alert` box for failed request,
#   you have to use `DetailStatus` in `enums.py`.
# Because `/` index page is filtering fail message by
#   `DetailStatus` Class
#
# To add a custom error type,
#   add a status on `DetailStatus` and
#   register to `DetailStatus._ALL_STATUS` tuple.
def lightfileshare_create(request):
    if request.method == "POST" and request.FILES:
        content = request.FILES["file"]

        posted_by = (
            request.user.username
            if request.user.is_authenticated
            else get_ranged_ip(request, start=0, end=4, mask="#")
        )
        password = request.POST.get("password")
        title = request.POST.get("title") or content.name

        # Filter unsafe filename segments defined in `localutils/unsafes/*`
        if safe_global_filename(filename=str(content.name)):
            return JsonResponse(
                {"message": DetailStatus.FailUnsafeFilename}, status=406
            )

        if title and content:
            # If user is logged in, set file private level to user's private level
            private_level = PrivateLevel.Public
            if request.user.is_authenticated:
                private_level = request.user.private_level

            SecretFile.objects.create(
                password=custom_hasher(password) if password else None,
                title=title,
                content=content,
                posted_by=posted_by,
                private_level=private_level,
            )
            return JsonResponse({"success": True}, status=200)
            # return HttpResponse(json.dumps({'success': True}), content_type='application/json', status=200) # redirect('/')
        return JsonResponse({"message": DetailStatus.FailNoFileUpload}, status=406)

    elif request.method == "POST" and not request.FILES:
        return JsonResponse({"message": DetailStatus.FailNoFileUpload}, status=406)

    return render(request, "lightfileshare/create.html")
