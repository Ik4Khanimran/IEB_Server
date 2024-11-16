# Common/management/commands/update_calibration_difference.py
from django.core.management.base import BaseCommand
from datetime import datetime
from Quality.models import QCalStatus
from mailer import send_mail


class Command(BaseCommand):
    help = 'Update calibration differences for all records'

    def handle(self, *args, **kwargs):
        today = datetime.now().date()
        records = QCalStatus.objects.all()
        updated_count = 0
        filtered_records = records.filter(next_cal_date__isnull=False)

        for record in filtered_records:
            next_cal_date = record.next_cal_date.date()
            difference = (next_cal_date - today).days

            # Save the calculated difference back to the record
            record.difference = difference
            record.save()

            updated_count += 1

        self.stdout.write(f'Successfully updated {updated_count} records.')

