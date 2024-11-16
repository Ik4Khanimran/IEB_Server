import os
from datetime import datetime, timezone
from typing import re

from celery import shared_task
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import QCalAgency, QGaugeType, QLocation, QCalStatus, QGaugeData, QGaugeDataTable, QMailerList
from .serializers import QCalAgencySerializer, QGaugeTypeSerializer, QLocationSerializer, QCalStatusSerializer, \
    QGaugeDataSerializer, QMailerListSerializer
from rest_framework.views import APIView
from Common.logging_config import setup_logger
logger = setup_logger(__name__)


@csrf_exempt
@api_view(['POST'])
def add_cal_agency(request):
    if request.method == 'POST':
        serializer = QCalAgencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new entry
            # print(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET'])
def get_cal_agencies(request):

    if request.method == 'GET':
        agencies = QCalAgency.objects.all().values()  # Fetch all the records
        agencies_list = list(agencies)  # Convert QuerySet to a list of dictionaries
        header_names = agencies[0].keys()  # Get the keys from the first record
        header_names_list = list(header_names)  # Convert to a list if needed

        # Create the response dictionary
        response_data = {
            'header_names': header_names_list,
            'values': agencies_list
        }

        return JsonResponse(response_data, safe=False)  # Return both data in the response


@csrf_exempt
@api_view(['DELETE'])
def delete_cal_agency(request, agency_id):
    # print(agency_id)
    try:
        agency = QCalAgency.objects.get(id=agency_id)
        agency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except QCalAgency.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['PUT'])
def edit_cal_agency(request, agency_id):
    try:
        agency = QCalAgency.objects.get(id=agency_id)
    except QCalAgency.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = QCalAgencySerializer(agency, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated entry
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def add_gauge_type(request):
    logger.info(f"Received data: {request.data}")
    if request.method == 'POST':
        serializer = QGaugeTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new entry
            # print(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET'])
def get_gauge_type(request):
    if request.method == 'GET':
        agencies = QGaugeType.objects.all().values()  # Fetch all the records
        agencies_list = list(agencies)  # Convert QuerySet to a list of dictionaries
        header_names = agencies[0].keys()  # Get the keys from the first record
        header_names_list = list(header_names)  # Convert to a list if needed

        # Create the response dictionary
        response_data = {
            'header_names': header_names_list,
            'values': agencies_list
        }

        return JsonResponse(response_data, safe=False)  # Return both data in the response

@csrf_exempt
@api_view(['DELETE'])
def delete_gauge_type(request, gauge_id):
    try:
        agency = QGaugeType.objects.get(id=gauge_id)
        agency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except QGaugeType.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['PUT'])
def edit_gauge_type(request, gauge_id):
    try:
        agency = QGaugeType.objects.get(id=gauge_id)
    except QGaugeType.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = QGaugeTypeSerializer(agency, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated entry
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def add_location(request):
    logger.debug(f"Request data: {request.data}")  # Log the incoming request data
    if request.method == 'POST':
        # print(request.data)
        serializer = QLocationSerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            serializer.save()  # Save the new entry
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.debug(f"Validation errors: {serializer.errors}")  # Log validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET'])
def get_location(request):
    if request.method == 'GET':
        agencies = QLocation.objects.all().values()  # Fetch all the records
        agencies_list = list(agencies)  # Convert QuerySet to a list of dictionaries
        header_names = agencies[0].keys()  # Get the keys from the first record
        header_names_list = list(header_names)  # Convert to a list if needed

        # Create the response dictionary
        response_data = {
            'header_names': header_names_list,
            'values': agencies_list
        }

        return JsonResponse(response_data, safe=False)  # Return both data in the response

@csrf_exempt
@api_view(['DELETE'])
def delete_location(request, gauge_id):
    try:
        agency = QLocation.objects.get(id=gauge_id)
        agency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except QLocation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['PUT'])
def edit_location(request, gauge_id):
    try:
        agency = QLocation.objects.get(id=gauge_id)
    except QLocation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = QLocationSerializer(agency, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated entry
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def add_cal_status(request):
    if request.method == 'POST':
        serializer = QCalStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new entry
            # print(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_cal_status(request):
    if request.method == 'GET':
        # Filter out records with invalid years (greater than 2100)
        agencies = QCalStatus.objects.filter(last_cal_date__year__lte=2100).values()
        agencies_list = list(agencies)  # Convert QuerySet to a list of dictionaries

        if agencies_list:
            header_names = agencies_list[0].keys()  # Get the keys from the first record
            header_names_list = list(header_names)  # Convert to a list if needed
        else:
            header_names_list = []

        # Create the response dictionary
        response_data = {
            'header_names': header_names_list,
            'values': agencies_list
        }

        return JsonResponse(response_data, safe=False)  # Return both data in the response

@csrf_exempt
@api_view(['DELETE'])
def delete_cal_status(request, agency_id):
    # print(agency_id)
    try:
        agency = QCalStatus.objects.get(id=agency_id)
        agency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except QCalStatus.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['PUT'])
def edit_cal_status(request, agency_id):
    try:
        agency = QCalStatus.objects.get(id=agency_id)
    except QCalStatus.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = QCalStatusSerializer(agency, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated entry
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def add_gauge_table(request):
    if request.method == 'POST':
        # Extract fields manually from the request
        # id = request.data.get('id')
        gauge_type_id = request.data.get('gauge_type_id')
        gauge_id_no = request.data.get('gauge_id_no')
        gauges = request.data.get('gauges')
        unit = request.data.get('unit')
        std_size = request.data.get('std_size')
        min_size = request.data.get('min_size') # Example of another field you may have
        max_size = request.data.get('max_size')
        go = request.data.get('go')
        nogo = request.data.get('nogo')
        std_tolerance = request.data.get('std_tolerance')
        min_tolerance = request.data.get('min_tolerance')
        max_tolerance = request.data.get('max_tolerance')
        min_range = request.data.get('min_range')
        max_range = request.data.get('max_range')
        least_count = request.data.get('least_count')
        min_acc = request.data.get('min_acc')
        max_acc = request.data.get('max_acc')
        location = request.data.get('location')
        frequency = request.data.get('frequency')
        act_1 = request.data.get('act_1')
        act_2 = request.data.get('act_2')
        act_3 = request.data.get('act_3')
        informer_1 = request.data.get('informer_1')
        informer_2 = request.data.get('informer_2')
        informer_3 = request.data.get('informer_3')
        authenticator_1 = request.data.get('authenticator_1')
        authenticator_2 = request.data.get('authenticator_2')

        print(gauge_type_id)
        gauge_data = {
            # 'id': id,
            'gauge_type': gauge_type_id,
            'gauge_id_no': gauge_id_no,
            'gauges': gauges,
            'unit': unit,
            'std_size': std_size,
            'min_size': min_size,
            'max_size': max_size,
            'go': go,
            'nogo': nogo,
            'std_tolerance':std_tolerance,
            'min_tolerance':min_tolerance,
            'max_tolerance': max_tolerance,
            'min_range': min_range,
            'max_range': max_range,
            'least_count': least_count,
            'min_acc': min_acc,
            'max_acc': max_acc,
            'location': location,
            'frequency': frequency,
            'act_1': act_1,
            'act_2': act_2,
            'act_3': act_3,
            'informer_1': informer_1,
            'informer_2': informer_2,
            'informer_3': informer_3,
            'authenticator_1': authenticator_1,
            'authenticator_2': authenticator_2

            # Add other fields as needed
        }
        print(gauge_data)

        # Use the serializer to validate and save the data
        serializer = QGaugeDataSerializer(data=gauge_data)

        if serializer.is_valid():
            print(1)
            serializer.save()  # Save the new entry to the database

            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return success response
        else:
            print(2)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return error if data is invalid


@csrf_exempt
@api_view(['GET'])
def get_gauge_table(request):
    if request.method == 'GET':
        table_type = request.GET.get('table_type', 'full')  # Optional query parameter

        if table_type == 'full':
            # Fetch all columns from the QGaugeData table
            agencies = QGaugeData.objects.all().values()
            agencies_list = list(agencies)
            header_names = agencies_list[0].keys() if agencies_list else []

        elif table_type == 'subset':
            # Fetch specified columns including least_count and frequency
            agencies = QGaugeData.objects.all().values(
                'gauge_id_no', 'gauges', 'unit', 'location',

            )
            agencies_list = list(agencies)
            header_names = agencies_list[0].keys() if agencies_list else []

        # Prepare the response data
        response_data = {
            'header_names': list(header_names),  # Convert to a list
            'values': agencies_list
        }

        return JsonResponse(response_data, safe=False)

@csrf_exempt
@api_view(['DELETE'])
def delete_gauge_table(request, agency_id):
    # print(agency_id)
    try:
        agency = QGaugeData.objects.get(id=agency_id)
        agency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except QGaugeData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return JsonResponse({'success': True})

@csrf_exempt
@api_view(['PUT'])
def edit_gauge_table(request, agency_id):
    try:
        agency = QGaugeData.objects.get(id=agency_id)
    except QGaugeData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = QGaugeDataSerializer(agency, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated entry
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def get_calibration_date(request, gauge_id):
#     try:
#         calibration = QCalStatus.objects.filter(gauge_id=gauge_id).latest('date_of_calibration') # Get latest calibration date
#         return Response({'last_cal_date': calibration.date_of_calibration})  # Return the last calibration date
#     except QCalStatus.DoesNotExist:
#         return Response({'last_cal_date': None}, status=404)  # Return None if no calibration found

@csrf_exempt
@api_view(['GET'])
def get_calibration_date(request):
    gauge_id = request.query_params.get('gauge_id', None)  # Get gauge_id from the query parameters

    try:
        if gauge_id:
            # Filter by gauge_id if it's provided
            calibrations = QCalStatus.objects.filter(gauge_id=gauge_id)
        else:
            # If no gauge_id is provided, return all calibrations
            calibrations = QCalStatus.objects.all()

        # Serialize the data
        serializer = QCalStatusSerializer(calibrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
def get_least_count_frequency(request):
    if request.method == 'GET':
        gauge_id = request.GET.get('gauge_id', None)

        if gauge_id:
            # Fetch least_count and frequency for the specified gauge_id_no
            gauge_data = QGaugeData.objects.filter(gauge_id_no=gauge_id).values('least_count', 'frequency').first()

            if gauge_data:
                return JsonResponse(gauge_data, safe=False)
            else:
                return JsonResponse({'error': 'Gauge not found'}, status=404)

        return JsonResponse({'error': 'Gauge ID is required'}, status=400)


def get_location_gauge_name(request):
    if request.method == 'GET':
        gauge_id = request.GET.get('gauge_id', None)

        if gauge_id:
            gauge_data = QGaugeData.objects.filter(gauge_id_no=gauge_id).values('gauges', 'location').first()

            if gauge_data:
                return JsonResponse(gauge_data, safe=False)
            else:
                return JsonResponse({'error': 'Gauge not found'}, status=404)

        return JsonResponse({'error': 'Gauge ID is required'}, status=400)


def create_report_folder(submissionTime, gauge_id):
    year = submissionTime.year
    month = submissionTime.month
    day = submissionTime.day

    main_folder_name = "Cal_Report"  # Change the main folder name
    sub_folder_date = f"{year}_{month:02}_{day:02}"

    cal_cert_path = os.path.join(os.getcwd(), main_folder_name, "Cal_Cert_Path", gauge_id, sub_folder_date)
    trace_cert_path = os.path.join(os.getcwd(), main_folder_name, "Trace_Cert_Path", gauge_id, sub_folder_date)

    print(f"Calibration Cert Path: {cal_cert_path}")
    print(f"Traceability Cert Path: {trace_cert_path}")

    os.makedirs(cal_cert_path, exist_ok=True)
    os.makedirs(trace_cert_path, exist_ok=True)



    return cal_cert_path, trace_cert_path

def save_report_files(files, cal_cert_path, trace_cert_path):
    try:
        if files.get('calibration_certificate'):
            calibration_cert_file_path = os.path.join(cal_cert_path, "calibration_certificate.pdf")
            with open(calibration_cert_file_path, 'wb') as f:
                f.write(files['calibration_certificate'].read())
            # print(f"Calibration certificate saved to {calibration_cert_file_path}")

        # Save traceability certificate file if it exists
        if files.get('traceability_certificate'):
            trace_cert_file_path = os.path.join(trace_cert_path, "traceability_certificate.pdf")
            with open(trace_cert_file_path, 'wb') as f:
                f.write(files['traceability_certificate'].read())
            # print(f"Traceability certificate saved to {trace_cert_file_path}")

    except Exception as e:
        print("Error saving report files:", e)
        return False

    return True


@csrf_exempt
@api_view(['POST'])
def submit_calibration_report(request):
    if request.method == 'POST':
        print("Received Data:", request.POST)
        print("Received Files:", request.FILES)

        def get_valid_value(value):
            return value if value and value.lower() != 'null' else None

        # Extract data from the request
        gauge_id = request.POST.get('gauge_id')
        calibration_frequency = request.POST.get('calibration_frequency')
        calibration_date = request.POST.get('calibration_date')
        next_calibration_date = request.POST.get('next_calibration_date')
        least_count = request.POST.get('least_count')
        frequency = request.POST.get('frequency')
        cal_certificate_no = get_valid_value(request.POST.get('calibration_cert_no'))
        calibrated_by = get_valid_value(request.POST.get('calibrated_by'))
        remark = get_valid_value(request.POST.get('remark'))
        verified_by = get_valid_value(request.POST.get('verified_by'))
        approved_by = get_valid_value(request.POST.get('approved_by'))

        calibration_certificate = request.FILES.get('calibration_certificate')
        traceability_certificate = request.FILES.get('traceability_certificate')

        try:
            # Update or create calibration status
            calibration_status, created = QCalStatus.objects.update_or_create(
                gauge_id=gauge_id,
                defaults={
                    'calibration_frequency': calibration_frequency,
                    'last_cal_date': calibration_date,
                    'next_cal_date': next_calibration_date,
                    'least_count': least_count,
                    'frequency': frequency,
                    'cal_certificate_no': cal_certificate_no,
                    'calibrated_by': calibrated_by,
                    'remark': remark,
                    'verified_by': verified_by,
                    'approved_by': approved_by,
                }
            )

            if calibration_certificate or traceability_certificate:
                submissionTime = datetime.strptime(calibration_date, '%Y-%m-%d')
                cal_cert_path, trace_cert_path = create_report_folder(submissionTime, gauge_id)

                # Save the files
                if save_report_files(
                    {'calibration_certificate': calibration_certificate, 'traceability_certificate': traceability_certificate},
                    cal_cert_path,
                    trace_cert_path
                ):
                    # Prepare paths for saving in the database
                    cal_cert_file_path = os.path.join(cal_cert_path, "calibration_certificate.pdf")
                    trace_cert_file_path = os.path.join(trace_cert_path, "traceability_certificate.pdf")

                    # Debug output to check the paths
                    print(f"Calibration Certificate Path: {cal_cert_file_path}")
                    print(f"Traceability Certificate Path: {trace_cert_file_path}")

                    # Save the paths in the database using the correct field names
                    calibration_status.cal_certificate_fpath = cal_cert_file_path
                    calibration_status.tracebility_cert_path = trace_cert_file_path

                    try:
                        calibration_status.save()  # Save the updated paths
                    except Exception as e:
                        print(f"Error saving calibration status: {e}")
                        return JsonResponse({"error": "Error saving file paths."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return JsonResponse({"error": "Error saving report files."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            message = "Calibration data submitted successfully!" + (" (New entry created)" if created else " (Existing entry updated)")
            return JsonResponse({"message": message}, status=status.HTTP_200_OK)

        except MultipleObjectsReturned:
            return JsonResponse({"error": "Multiple records found for the given gauge_id. Please resolve the duplicates."}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def get_cal_report_result(request):
    gauge_id = request.GET.get('gauge_id')
    print(f"Received gauge_id: {gauge_id}")  # Debug log
    try:
        calibration_status = QCalStatus.objects.get(gauge_id=gauge_id)
        serializer = QCalStatusSerializer(calibration_status)
        print(f"Retrieved calibration data: {serializer.data}")  # Debug log
        return Response(serializer.data, status=status.HTTP_200_OK)
    except QCalStatus.DoesNotExist:
        print("Calibration data not found")  # Debug log
        return Response({"error": "Calibration data not found"}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['GET'])
def get_cal_mailer_list(request):
    if request.method == 'GET':
        mailer_list = QMailerList.objects.all().values()  # Ensure this is the correct model
        mailer_list_data = list(mailer_list)  # Convert QuerySet to a list of dictionaries

        if mailer_list_data:  # Check if there is data
            header_names = mailer_list_data[0].keys()  # Get keys from the first record
        else:
            header_names = []  # Handle empty case

        response_data = {
            'header_names': list(header_names),  # Convert to list
            'values': mailer_list_data
        }

        return JsonResponse(response_data, safe=False)

@csrf_exempt
@api_view(['DELETE'])
def delete_cal_mailer_entry(request, entry_id):
    try:
        entry = QMailerList.objects.get(id=entry_id)
        entry.delete()
        return JsonResponse({'message': 'Entry deleted successfully!'}, status=204)
    except QMailerList.DoesNotExist:
        return JsonResponse({'error': 'Entry not found!'}, status=404)

@csrf_exempt
@api_view(['PUT'])
def edit_cal_mailer_list(request, entry_id):
    try:
        entry = QMailerList.objects.get(id=entry_id)
    except QMailerList.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = QMailerListSerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated entry
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def add_cal_mail_entry(request):
    if request.method == 'POST':
        serializer = QMailerListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new entry
            # print(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     ===============


# @csrf_exempt
# @api_view(['GET'])
# def get_gaugeid_mail(request):
#     if request.method == 'GET':
#         mailer_list = QGaugeIdMail.objects.all().values()  # Ensure this is the correct model
#         mailer_list_data = list(mailer_list)  # Convert QuerySet to a list of dictionaries
#
#         if mailer_list_data:  # Check if there is data
#             header_names = mailer_list_data[0].keys()  # Get keys from the first record
#         else:
#             header_names = []  # Handle empty case
#
#         response_data = {
#             'header_names': list(header_names),  # Convert to list
#             'values': mailer_list_data
#         }
#
#         return JsonResponse(response_data, safe=False)
#
# @csrf_exempt
# @api_view(['DELETE'])
# def delete_gaugeid_mail(request, entry_id):
#     try:
#         entry = QGaugeIdMail.objects.get(id=entry_id)
#         entry.delete()
#         return JsonResponse({'message': 'Entry deleted successfully!'}, status=204)
#     except QMailerList.DoesNotExist:
#         return JsonResponse({'error': 'Entry not found!'}, status=404)
#
# @csrf_exempt
# @api_view(['PUT'])
# def edit_gaugeid_mail(request, entry_id):
#     try:
#         entry = QGaugeIdMail.objects.get(id=entry_id)
#     except QGaugeIdMail.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'PUT':
#         serializer = QGaugeIdMailSerializer(entry, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()  # Save the updated entry
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# @csrf_exempt
# @api_view(['POST'])
# def add_gaugeid_mail(request):
#     if request.method == 'POST':
#         serializer = QGaugeIdMailSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()  # Save the new entry
#             # print(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




