import os
import django
from datetime import datetime

# Set up Django environment
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Greaves.Greaves.settings')
# django.setup()

from Quality.models import QCalStatus

def update_calibration_difference():
    # Get today's date
    today = datetime.now().date()

    # Get all records that need updating
    records = QCalStatus.objects.all()

    updated_count = 0  # Count how many records were updated

    # Loop through the records and calculate the difference
    for record in records:
        if record.next_cal_date:
            # Calculate the difference in days
            difference = (record.next_cal_date.date() - today).days

            # Update the record's difference field
            record.difference = difference
            record.save()

            updated_count += 1

    print(f'Successfully updated {updated_count} records')

if __name__ == '__main__':
    update_calibration_difference()
