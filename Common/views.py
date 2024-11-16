from django.middleware.csrf import get_token
from django.http import JsonResponse
import logging
import os
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from datetime import datetime

from Quality.models import QCalStatus
# @ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    print(csrf_token)
    return JsonResponse({'csrfToken': csrf_token})

def setup_logger(name, log_file='logs/messages.log', level=logging.DEBUG):
    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a file handler
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
# $ ATP.views  # INFO - Checksheet opened successfully with data: 123331 - Module: ATP.views - Function: checksheet_data

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s # %(levelname)s $ %(name)s  - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger



def update_calibration_difference(request):
    # Get today's date
    today = datetime.now().date()

    # Get all records that need updating
    records = QCalStatus.objects.all()

    updated_count = 0  # Count how many records were updated

    # Filter records where next_cal_date is not null
    filtered_records = records.filter(next_cal_date__isnull=False)

    # Loop through the filtered records and calculate the difference
    for record in filtered_records:
        next_cal_date = record.next_cal_date.date()  # Convert datetime to date
        difference = (next_cal_date - today).days

        # Save the calculated difference back to the record
        record.difference = difference
        record.save()  # Save the updated record to the database

        updated_count += 1

    print(f'Successfully updated {updated_count} records.')
    # return HttpResponse(f'Successfully updated {updated_count} records.')