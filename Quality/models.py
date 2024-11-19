import os

from django.db import models

class QCalAgency(models.Model):
    cal_agency = models.CharField(max_length=50)  # Assume this is a unique identifier
    name = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    contact1 = models.CharField(max_length=50, blank=True, null=True)
    contact2 = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'Q_cal_agency'
        managed = False  # Prevent Django from trying to manage the table

class QGaugeType(models.Model):
    gauge_type = models.CharField(max_length=255)  # Set a max_length that suits your needs
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID field

    class Meta:
        db_table = 'Q_gauge_types'  # This will link it to the existing table
        verbose_name = 'Gauge Type'
        verbose_name_plural = 'Gauge Types'

    def __str__(self):
        return self.gauge_type

class QLocation(models.Model):
    location = models.CharField(max_length=50)
    name = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    contact_person1 = models.CharField(max_length=50, null=True, blank=True)
    contact_person2 = models.CharField(max_length=50, null=True, blank=True)
    contactp_mail1 = models.EmailField(max_length=50, null=True, blank=True)
    contactp_mail2 = models.EmailField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'Q_location'  # This specifies the table name in the database
        ordering = ['id']  # Optional: default ordering for querysets

    def __str__(self):
        return self.location

class QCalStatus(models.Model):
    gauge_id = models.CharField(max_length=50, null=True, blank=True)
    cal_agency = models.CharField(max_length=50, null=True, blank=True)
    last_cal_date = models.DateTimeField(null=True, blank=True)
    next_cal_date = models.DateTimeField(null=True, blank=True)
    cal_certificate_no = models.CharField(max_length=50, null=True, blank=True)
    cal_certificate_fpath = models.CharField(max_length=50, null=True, blank=True)
    tracebility_cert_path = models.CharField(max_length=50, null=True, blank=True)
    calibrated_by = models.CharField(max_length=50, null=True, blank=True)
    remark = models.CharField(max_length=50, null=True, blank=True)
    verified_by = models.CharField(max_length=50, null=True, blank=True)
    approved_by = models.CharField(max_length=50, null=True, blank=True)
    id = models.AutoField(primary_key=True)  # Use AutoField for the primary key
    difference = models.IntegerField(default=0)

    class Meta:
        db_table = 'Q_cal_status'  # This specifies the table name in the database
        ordering = ['gauge_id']  # Optional: default ordering for querysets

    def __str__(self):
        return self.gauge_id if self.gauge_id else "No Gauge ID"

class QGaugeData(models.Model):
    gauge_type = models.ForeignKey('QGaugeType', on_delete=models.RESTRICT)
    gauge_id_no = models.CharField(max_length=50)
    id = models.AutoField(primary_key=True)  # Use AutoField for the primary key
    gauges = models.CharField(max_length=50, blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    std_size = models.CharField(max_length=50, blank=True, null=True)
    min_size = models.CharField(max_length=50, blank=True, null=True)
    max_size = models.CharField(max_length=50, blank=True, null=True)
    go = models.CharField(max_length=50, blank=True, null=True)
    nogo = models.CharField(max_length=50, blank=True, null=True)
    std_tolerance = models.CharField(max_length=50, blank=True, null=True)
    min_tolerance = models.CharField(max_length=50, blank=True, null=True)
    max_tolerance = models.CharField(max_length=50, blank=True, null=True)
    min_range = models.CharField(max_length=255, blank=True, null=True)
    max_range = models.CharField(max_length=255, blank=True, null=True)
    least_count = models.CharField(max_length=50, blank=True, null=True)
    min_acc = models.CharField(max_length=50, blank=True, null=True)
    max_acc = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    frequency = models.IntegerField(blank=True, null=True)
    act_1 = models.CharField(max_length=255, blank=True, null=True)
    act_2 = models.CharField(max_length=255, blank=True, null=True)
    act_3 = models.CharField(max_length=255, blank=True, null=True)
    informer_1 = models.CharField(max_length=255, blank=True, null=True)
    informer_2 = models.CharField(max_length=255, blank=True, null=True)
    informer_3 = models.CharField(max_length=255, blank=True, null=True)
    authenticator_1 = models.CharField(max_length=255, blank=True, null=True)
    authenticator_2 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Q_gauge_data_table'

class QGaugeDataTable(models.Model):
    gauge_id_no = models.IntegerField()                # Reference to gauge ID, assuming it's an integer
    gauges = models.CharField(max_length=100)         # Name of the gauge
    unit = models.CharField(max_length=50)             # Measurement unit
    location = models.CharField(max_length=100)        # Location of the gauge
    # Add other fields as necessary

    class Meta:
        unique_together = (('gauge_id_no', 'gauges'),)  # Ensure uniqueness based on gauge ID and gauge name

    def __str__(self):
        return self.gauges  # Returns the gauge name as the string representation

class QMailerList(models.Model):
    id = models.AutoField(primary_key=True)
    mail_id = models.CharField(max_length=50)
    # role = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    # gauge_id = models.CharField(max_length=50)

    class Meta:
        db_table = 'Q_mailer_list'  # Ensure this matches your database table name
        ordering = ['id']  # Optional: order by id by default

    def __str__(self):
        return f"{self.name} - {self.mail_id}"


def calibration_cert_path(instance, filename):
    # Dynamic path generation for calibration certificates
    return os.path.join('Cal_Cert_Path', instance.gauge_id, instance.calibration_date, filename)

def traceability_cert_path(instance, filename):
    # Dynamic path generation for traceability certificates
    return os.path.join('Trace_Cert_Path', instance.gauge_id, instance.traceability_date, filename)

class CalibrationReport(models.Model):
    gauge_id = models.CharField(max_length=255)
    calibration_date = models.DateField()
    traceability_date = models.DateField()
    # Calibration certificate
    calibration_certificate = models.FileField(upload_to=calibration_cert_path)
    # Traceability certificate
    traceability_certificate = models.FileField(upload_to=traceability_cert_path)

    def __str__(self):
        return f"Calibration Report for {self.gauge_id}"

