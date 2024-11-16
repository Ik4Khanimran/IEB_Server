# Users/urls.py
from django.urls import path
from . import views

app_name = 'ATP'

urlpatterns = [
    path('opn_checksheet/', views.opn_checksheet, name='opn_checksheet'),
    path('checksheet_data/', views.checksheet_data, name='checksheet_data'),
    path('audit_checksheet/', views.audit_checksheet, name='audit_checksheet'),
    path('rework_checksheet/', views.rework_checksheet, name='rework_checksheet'),
    path('opn_rework_checksheet/', views.opn_rework_checksheet, name='opn_rework_checksheet'),
    path('opn_audit_checksheet/', views.opn_audit_checksheet, name='opn_audit_checksheet'),
    path('opn_ops_st10/', views.opn_ops_st10, name='opn_ops_st10'),
    path('engine_checksheet_result/', views.engine_checksheet_result, name='engine_checksheet_result'),
    # path('engine_checksheet_audit/', views.engine_checksheet_audit, name='engine_checksheet_audit'),
    path('get_drdwn_val/', views.get_drdwn_val, name='get_drdwn_val'),
    path('database_connection/', views.database_connection, name='database_connection'),
    path('data_delete/', views.data_delete, name='data_delete'),
    path('data_edit/', views.data_edit, name='data_edit'),
    path('data_new_entry/', views.data_new_entry, name='data_new_entry'),
    path('save_new_entry/', views.save_new_entry, name='save_new_entry'),
    path('assemblyop_submit/', views.assemblyop_submit, name='assemblyop_submit'),
    path('get_assemblyop_result/', views.get_assemblyop_result, name='get_assemblyop_result'),
    path('assemblyop_hold/', views.assemblyop_hold, name='assemblyop_hold'),

]