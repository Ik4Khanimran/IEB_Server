from django.conf.urls.static import static
from django.urls import path
# from .views import add_cal_agency, get_cal_agencies
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('add_cal_agency/', views.add_cal_agency, name='add_cal_agency'),
    path('get_cal_agencies/', views.get_cal_agencies, name='get_cal_agencies'),
    path('delete_cal_agency/<int:agency_id>/', views.delete_cal_agency, name='delete_cal_agency'),
    path('edit_cal_agency/<int:agency_id>/', views.edit_cal_agency, name='edit_cal_agency'),

    path('add_gauge_type/', views.add_gauge_type, name='add_gauge_type'),
    path('get_gauge_type/', views.get_gauge_type, name='get_gauge_type'),
    path('delete_gauge_type/<int:gauge_id>/', views.delete_gauge_type, name='delete_gauge_type'),
    path('edit_gauge_type/<int:gauge_id>/', views.edit_gauge_type, name='edit_gauge_type'),

    path('add_location/', views.add_location, name='add_location'),
    path('get_location/', views.get_location, name='get_location'),
    path('delete_location/<int:location_id>/', views.delete_location, name='delete_location'),
    path('edit_location/<int:location_id>/', views.edit_location, name='edit_location'),

    path('add_cal_status/', views.add_cal_status, name='add_cal_status'),
    path('get_cal_status/', views.get_cal_status, name='get_cal_status'),
    path('delete_cal_status/<int:agency_id>/', views.delete_cal_status, name='delete_cal_status'),
    path('edit_cal_status/<int:agency_id>/', views.edit_cal_status, name='edit_cal_status'),

    path('add_gauge_table/', views.add_gauge_table, name='add_gauge_table'),
    path('get_gauge_table/', views.get_gauge_table, name='get_gauge_table'),
    path('delete_gauge_table/<int:agency_id>/', views.delete_gauge_table, name='delete_gauge_table'),
    path('edit_gauge_table/<int:agency_id>/', views.edit_gauge_table, name='edit_gauge_table'),

   # path('get_calibration_date/<int:id>/', views.get_calibration_date, name='get_calibration_date'), # pervious link
    path('get_calibration_date/', views.get_calibration_date, name='get_calibration_date'),
    path('get_least_count_frequency/', views.get_least_count_frequency, name='get_least_count_frequency'),
    path('submit_calibration_report/', views.submit_calibration_report, name='submit_calibration_report'),
    path('get_location_gauge_name/', views.get_location_gauge_name, name='get_location_gauge_name'),

    path('get_cal_report_result/', views.get_cal_report_result, name='get_cal_report_result'),
    path('get_cal_mailer_list/', views.get_cal_mailer_list, name='get_cal_mailer_list'),
    path('delete_cal_mailer_entry/<int:entry_id>/', views.delete_cal_mailer_entry, name='delete_cal_mailer_entry'),
    path('edit_cal_mailer_list/<int:entry_id>/', views.edit_cal_mailer_list, name='edit_cal_mailer_list'),
    path('add_cal_mail_entry/', views.add_cal_mail_entry, name='add_cal_mail_entry'),

    path('get_calibration_report/', views.get_calibration_report, name='get_calibration_report'),


]

# Serve media files in development mode (only when DEBUG is True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

