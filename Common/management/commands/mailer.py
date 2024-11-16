# Common/management/commands/update_calibration_difference.py
from django.core.management.base import BaseCommand
from Quality.models import QCalStatus
from Mailer.views import SendEmailView


class Command(BaseCommand):
    help = 'Update calibration differences for all records'

    def handle(self, *args, **kwargs):
        records = QCalStatus.objects.all()

        updated_count = 0  # Count how many records were updated
        filtered_records = records.filter(difference__isnull=False)

        # for record in filtered_records:
        #     if record.difference < 0:
        #         SendEmailView.email_send(record.gauge_id)

        for record in filtered_records:
            gauge_id = record.gauge_id

            if record.difference == 30:
                SendEmailView.email_send(record.gauge_id, ['act_1', 'act_2', 'act_3'])

            elif record.difference == 15:
                SendEmailView.email_send(record.gauge_id, ['informer_1', 'informer_2', 'informer_3'])

            elif record.difference == 5:
                SendEmailView.email_send(record.gauge_id, ['authenticator_1', 'authenticator_2'])

        self.stdout.write(f'Successfully updated {updated_count} records.')

