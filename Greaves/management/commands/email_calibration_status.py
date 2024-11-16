import os
import django
from datetime import datetime

from Quality.models import QCalStatus
from Greaves.Mailer.views import send_mail
def email_callibration_status():
    # Get all records that need updating
    records = QCalStatus.objects.all()

    updated_count = 0  # Count how many records were updated

    # Loop through the records and calculate the difference
    for record in records:
        if record.difference >10 :
            # Calculate the difference in days
            print(f"try one {record['gauge_id']}")
            print(f"try two {record.gauge_id}")
            send_mail(record['gauge_id'])


if __name__ == '__main__':
    email_callibration_status()
