from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from localutils.password_validator import validate_password

from .models import CustomUser

# Create your views here.


def customauth_register(request):
    if request.method == "POST":
        username  = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'customauth/register.html', {
                'fail_reason': "Passwords are not equal",
            })

        valid_or_reason = validate_password(password1)
        if valid_or_reason == True:
            try:
                user_with_this_username = CustomUser.objects.get(username=username)
                return render(request, 'customauth/register.html', {
                    'fail_reason': "Username already occupied",
                })

            except CustomUser.DoesNotExist:
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password1,
                )
                return redirect('/?info=Please contact site admin to activate your account')

        return render(request, 'customauth/register.html', {
            'fail_reason': valid_or_reason,
        })
    return render(request, 'customauth/register.html', {
        'fail_reason': False,
    })

def customauth_login(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('/')

        return render(request, 'customauth/login.html', {
            'fail_reason': "Login Credential Not Exists",
        })
    return render(request, 'customauth/login.html', {
        'fail_reason': None,
    })

def customauth_logout(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)
