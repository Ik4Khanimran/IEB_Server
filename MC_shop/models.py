from django.db import models

# Create your models here.

class McMachinelist(models.Model):
    machine_name = models.TextField()

    class Meta:
        managed = False
        db_table = 'MC_machinelist'


class McPartname(models.Model):
    partname = models.TextField()

    class Meta:
        managed = False
        db_table = 'MC_partname'


class McProductiondata(models.Model):
    machine_name = models.TextField(blank=True, null=True)
    cell_name = models.TextField(blank=True, null=True)
    shift = models.TextField(blank=True, null=True)
    part_name = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    produced_qty = models.IntegerField(blank=True, null=True)
    rejected_qty = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MC_productiondata'

