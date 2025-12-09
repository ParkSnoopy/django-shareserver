from django.urls import path
from .views import (
    customauth_register,
    customauth_login,
    customauth_logout,
)



urlpatterns = [
    path('login/', customauth_login), 
    path('logout/', customauth_logout),
    path('register/', customauth_register), 
]
