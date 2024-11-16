from django.urls import path
# from .views import add_cal_agency, get_cal_agencies
from . import views
urlpatterns = [
    path('abc/', views.abc, name='abc'),
]
