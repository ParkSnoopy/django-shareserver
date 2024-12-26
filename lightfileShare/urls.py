from django.urls import path
from .views import (
    lightfileshare_home, 
    lightfileshare_details, 
    lightfileshare_create, 
)



urlpatterns = [
    path('', lightfileshare_home), 
    path('details/', lightfileshare_details), 
    path('create/', lightfileshare_create), 
    
]
