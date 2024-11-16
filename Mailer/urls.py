from django.urls import path
from .views import SendEmailView, email_callibration_status  # Make sure this import matches the class name

urlpatterns = [
    path('send-email/', SendEmailView.as_view(), name='send_email'),
    path('email/', email_callibration_status, name='email'),
]
