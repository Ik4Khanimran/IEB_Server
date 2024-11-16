from django.urls import path
from . import views

app_name = 'Operations'

urlpatterns = [
    path('get_esn_data/', views.get_esn_data, name='get_esn_data'),
    path('update_location/', views.update_location, name='update_location'),
]
