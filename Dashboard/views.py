from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
# from Greaves.ATP.models import EngResultHeader, EngLocation
from ATP.models import EngResultHeader, EngLocation, EngineAsslyOp
from django.db.models import Count, Q, Min, Max
import logging
import pytz
import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)
from collections import Counter
# Create your views here.

@csrf_exempt
def get_data(request):
    if request.method == 'POST':
        try:
            logger.info('POST request received')
            data = json.loads(request.body)
            year = data['year']
            month = data['month']
            logger.info(f'Request data received: {data}')
        except json.JSONDecodeError as e:
            logger.error(f'Failed to decode JSON: {e}')
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except KeyError as e:
            logger.error(f'Missing key in request data: {e}')
            return JsonResponse({'error': 'Missing required parameters'}, status=400)


        try:
            filter_data_xcl = EngLocation.objects.filter(
                Q(st30_date__year=year) & Q(st30_date__month=month)
            ).values()
            data_xcl = list(filter_data_xcl)
            logger.info(f'XCL data fetched')

            filter_data_csr = EngResultHeader.objects.filter(
                Q(timestamp__year=year) & Q(timestamp__month=month)
            ).values('esn', 'timestamp', 'bom_srno_id__bom').order_by('timestamp')
            data_csr = list(filter_data_csr)
            logger.info(f'CSR data fetched')

            filter_data_test = EngLocation.objects.filter(
                Q(st20_date__year=year) & Q(st20_date__month=month) & Q(st20_status=True)
            ).values('esn', 'st20_date', 'bom', 'st20_status').order_by('st20_date')
            data_test = list(filter_data_test)
            logger.info(f'TEST data fetched')

            filter_data_assly = EngineAsslyOp.objects.filter(
                Q(timestamp__year=year) & Q(timestamp__month=month) & Q(status=True)
            ).values('esn', 'timestamp', 'bom_id__bom', 'status').order_by('timestamp')
            data_assly = list(filter_data_assly)
            logger.info(f'ASSLY data fetched')

            # Fetch and aggregate data from the database
            filter_data01 = EngLocation.objects.values('esn', 'bom', 'cur_loc').filter(
                Q(cur_loc__gte=5) & Q(cur_loc__lt=50)
            ).annotate(count=Count('bom'))


            # Convert queryset to a list of dictionaries
            filter_data01 = list(filter_data01)
            logger.info(f'Aggregated data fetched: {filter_data01}')

        except Exception as e:
            logger.error(f'An error occurred while processing the data: {e}')
            return JsonResponse({'error': 'Internal server error'}, status=500)

        return JsonResponse({
            'status': 'success',
            'data_xcl': data_xcl,
            'data_csr': data_csr,
            'data_test': data_test,
            'data_assly': data_assly,
            'dataset_01': filter_data01,
            'message': 'API received for dashboard, response sent'
        })
    return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def download_data(request):
    if request.method == 'POST':
        try:
            logger.info('POST request received')
            data = json.loads(request.body)
            # Extract values
            selected_date = data.get("selectedDate")
            selected_area = data.get("selectedArea")

            # Parse the selectedDate to extract month and year
            date_object = datetime.datetime.strptime(selected_date, "%Y-%m-%dT%H:%M:%S.%fZ")  # Parse ISO 8601 format
            month = date_object.strftime("%m")  # Month as a zero-padded number
            year = date_object.strftime("%Y")   # Year

            print(month, year, selected_area)

            if selected_area == 'CSR' :
                filter_data_csr = EngResultHeader.objects.filter(
                    Q(timestamp__year=year) & Q(timestamp__month=month)
                ).values('esn', 'timestamp', 'bom_srno_id__bom').order_by('timestamp')
                data = list(filter_data_csr)
                logger.info(f'CSR data downloaded')

            if selected_area == 'Assembly' :
                filter_data_assly = EngineAsslyOp.objects.filter(
                    Q(timestamp__year=year) & Q(timestamp__month=month) & Q(status=True)
                ).values('esn', 'timestamp', 'bom_id__bom', 'status').order_by('timestamp')
                data = list(filter_data_assly)
                logger.info(f'CSR data downloaded')

            return JsonResponse({
                'status': 'success',
                'data': data,
                'message': 'API received to download data, response sent'
            })
        except Exception as e:
            logger.error(f'An error occurred while processing the data: {e}')
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return JsonResponse( status=400)




