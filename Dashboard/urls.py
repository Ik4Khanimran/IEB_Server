# Users/urls.py
from django.urls import path
from . import views

app_name = 'Dashboard'

urlpatterns = [
    path('get_data/', views.get_data, name='get_data'),
    path('download_data/', views.download_data, name='download_data'),
]
