from django.core.mail import send_mail
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmailSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Quality.models import QCalStatus
from Quality.models import QGaugeData
# from Greaves.Mailer.views import send_mail


@method_decorator(csrf_exempt, name='dispatch')
class SendEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            to_email = serializer.validated_data['to_email']
            try:
                # send_mail(subject, message, 'vr.me1@greavescotton.com', [to_email])
                send_mail(subject, message, 'vr.me1@greavescotton.com', to_email)

                return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def email_send(gauge_id, email_field_names):

        # Fetch records filtered by gauge_id_no
        mail_records = QGaugeData.objects.filter(gauge_id_no=gauge_id).values('gauge_type_id', 'gauge_id_no', 'act_1', 'act_2', 'act_3')

        # Check if any records exist
        if mail_records.exists():
            # Iterate over the queryset and print the gauge_id_no field
            for record in mail_records:
                # print(f"Gauge ID No: {record['gauge_id_no']}")
                # print(f"mail id 1: {record['act_1']}")

                # act_1_email = record.get('act_1')
                # act_2_email = record.get('act_2')
                # act_3_email = record.get('act_3')
                # to_email = []
                # if act_1_email:
                #     to_email.append(act_1_email)
                # if act_2_email:
                #     to_email.append(act_2_email)
                # if act_3_email:
                #     to_email.append(act_3_email)

                to_email = []

                # Add emails to the list based on the available fields
                for field in email_field_names:
                    email = record.get(field)
                    if email:
                        to_email.append(email)

                if to_email:
                    subject = f"New Calibration Due for Gauge ID: {record['gauge_id_no']}"
                    message = f"New Calibration Due for Gauge ID: {record['gauge_id_no']}"

                    try:
                        # Send the email
                        send_mail(subject, message, 'vr.me1@greavescotton.com', to_email)
                        print(f"Email sent to: {', '.join(to_email)}")
                    except Exception as e:
                        print(f"Error sending email: {e}")
                else:
                    print(f"No email addresses available for Gauge ID: {record['gauge_id_no']}")



def email_callibration_status(request):
    # Get all records that need updating
    records = QCalStatus.objects.all()

    updated_count = 0  # Count how many records were updated
    filtered_records = records.filter(difference__isnull=False)

    # for record in filtered_records:
    #     if record.difference < 0:
    #         SendEmailView.email_send(record.gauge_id)

    for record in filtered_records:
        gauge_id = record.gauge_id

        if record.difference == 30:
            SendEmailView.email_send(gauge_id, ['act_1', 'act_2', 'act_3'])

        elif record.difference == 15:
            SendEmailView.email_send(gauge_id, ['informer_1', 'informer_2', 'informer_3'])

        elif record.difference == 5:
            SendEmailView.email_send(gauge_id, ['authenticator_1', 'authenticator_2'])

    return JsonResponse({'message': 'Email notifications sent successfully for updated records.'}, status=200)
