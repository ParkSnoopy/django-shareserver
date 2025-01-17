from django.shortcuts import render, redirect
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse

from localutils.hasher import custom_hasher, check_password
from localutils.filename_validator import safe_global_filename
from localutils.secretfile_filter import secretfile_filter
from localutils.private_level import PrivateLevel
from localutils.ip_tools import get_ranged_ip

from .models import SecretFile
from .enums import DetailStatus

import json

# APH = settings.MY_ACCESS_PERMISSION_HANDLER
FPH = settings.MY_FILE_PERMISSION_HANDLER

# Create your views here.


def lightfileshare_home(request):

    SecretFile.objects.remove_not_exist()
    SecretFile.objects.remove_expired()

    private_level = PrivateLevel.Public
    if request.user.is_authenticated:
        private_level = request.user.private_level

    return render(request, 'lightfileShare/index.html', {
        'objs': SecretFile.objects.filter(private_level__lte=private_level).order_by("id"), #.values('id', 'title', 'posted_by', 'expire_at', 'password', 'content'),
        'alert': DetailStatus.parse( request.GET.get('fail') ),
        'info': request.GET.get('info'),
        'status': DetailStatus,
    })


def lightfileshare_details(request):
    if request.method == 'POST':

        private_level = PrivateLevel.Public
        if request.user.is_authenticated:
            private_level = request.user.private_level

        pk = request.POST.get('id')

        if pk:
            try:
                secretfile = SecretFile.objects.get(pk=pk)
                filename = secretfile.filename
                # print(f"  POST(get) - {private_level=} CMP {secretfile.private_level=} ; {filename=}")

                if private_level < secretfile.private_level:
                    return redirect(f'/?fail={DetailStatus.FailNoPermission}')

                if secretfile.password:
                    password = request.POST.get('password', '')

                    if check_password( password, secretfile.password ):

                        FPH.set_permission( request, filename )
                        return redirect(settings.LIGHTFILE_LOAD_URL + filename) # FileResponse( open( filepath, 'rb' ) )

                    # print(f"{password=} ; {secretfile.password=} ; check_password={check_password( password, secretfile.password )}")

                    return redirect(f'/?fail={DetailStatus.FailPassword}')

                else:
                    FPH.set_permission( request, filename )
                    return redirect(settings.LIGHTFILE_LOAD_URL + filename) # FileResponse( open( filepath, 'rb' ) )

            except SecretFile.DoesNotExist:
                return redirect(f'/?fail={DetailStatus.FailNoFile}')

    return redirect(f'/?fail={DetailStatus.FailWrongMethod}')


def lightfileshare_create(request):
    if request.method == 'POST' and request.FILES:
        content = request.FILES['file']

        posted_by = request.user.username if request.user.is_authenticated else get_ranged_ip(request, start=0, end=3, mask='#')
        password = request.POST.get('password')
        title = request.POST.get('title') or content.name

        filename, unsafe_word = safe_global_filename(filename=str(content.name))

        if not filename:
            return JsonResponse(
                {
                    'success': False,
                    'message': f"filename '{content.name}' is considered an important system file",
                },
                status=406,
            )
            '''
            return render(
                request,
                'lightfileShare/failure.html',
                {
                    'redirect': 'create',
                    'fail_reason': f"filename '{content.name}' is considered an important system file",
                    'fail_explain': f"please consider replace '{unsafe_word}' to other common word",
                }
            )
            '''

        # print(f"CREATE: {request.POST=}")

        if title and content:
            # If user is logged in, set file private level to user's private level
            private_level = PrivateLevel.Public
            if request.user.is_authenticated:
                private_level = request.user.private_level

            SecretFile.objects.create(
                password = custom_hasher(password) if password else None,
                title=title,
                content=content,
                posted_by=posted_by,
                private_level=private_level,
            )
            return JsonResponse({'success': True}, status=200)
            # return HttpResponse(json.dumps({'success': True}), content_type='application/json', status=200) # redirect('/')
        return JsonResponse({'message': "no file uploaded"}, status=400)
    return render(request, 'lightfileShare/create.html')
