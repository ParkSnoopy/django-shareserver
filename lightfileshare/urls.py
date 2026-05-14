from django.urls import path
from .views import (
    lightfileshare_home, 
    lightfileshare_details, 
    lightfileshare_create,
    lightfileshare_download,
)



urlpatterns = [
    path('', lightfileshare_home), 
    path('details/', lightfileshare_details), 
    path('download/<int:pk>/', lightfileshare_download),
    path('create/', lightfileshare_create), 
]
