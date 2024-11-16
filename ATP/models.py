# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone



class EngModel(models.Model):
    srno = models.AutoField(primary_key=True)
    engmodel = models.CharField(unique=True, max_length=20, help_text="addition of model & application")
    model = models.CharField(max_length=20, help_text="e.g 3G, 4G, 6G, D3V6, D3V8, NEWD")
    application = models.CharField(max_length=20, help_text="e.g Genset, Marine, FMUL, Others")
class EngCheckpoint(models.Model):
    checkpoint_id = models.AutoField(primary_key=True)
    checkpoint = models.TextField(help_text="Hint : Describe the checkpoint requirement ")
    type = models.CharField(max_length=20, help_text="Hint : for tick mark, select checkbox, have any option select dropdown & if want to type value select textbox")
    options = models.CharField(max_length=50, blank=True, null=True, help_text="Hint : Between each options kept ' /'  ")
class Operation(models.Model):
    stno = models.AutoField(primary_key=True)
    op_name = models.CharField(unique=True, max_length=20)
    op_detail = models.TextField(unique=True)
class CheckpointMap(models.Model):
    engmodel = models.ForeignKey(EngModel, models.DO_NOTHING, db_column='engmodel', to_field='engmodel', help_text="Select the eng model from dropdown")
    # bom = models.ForeignKey(BomList, models.DO_NOTHING, db_column='bom', to_field='bom', help_text="Select the BOM no from dropdown")
    checkpoint = models.ForeignKey('EngCheckpoint', models.DO_NOTHING, help_text="Select the Checkpoint from dropdown")
    seq_no = models.IntegerField(help_text="Give the no in which it will occured in Checksheet")
    stno = models.ForeignKey('Operation', models.DO_NOTHING, db_column='stno', help_text="Select the station number from dropdown")
    map_status = models.BooleanField(help_text="To keep it in checksheet, check checkbox")
    map_date = models.DateTimeField(help_text="Select date")
    map_by = models.IntegerField(help_text="provide employee Id")
    unmap_date = models.DateTimeField(blank=True, null=True, help_text="Select date")
    unmap_by = models.IntegerField(blank=True, null=True, help_text="provide employee Id")
class EngResultCheckpoints(models.Model):
    result = models.ForeignKey('EngResultHeader', models.DO_NOTHING, to_field='result_id')
    data_id = models.CharField(unique=True, max_length=25)
    checkpoint = models.ForeignKey(EngCheckpoint, models.DO_NOTHING)
    checkpoint_status = models.CharField(max_length=255)
    seq_no = models.IntegerField(blank=True, null=True)
class BomList(models.Model):
    srno = models.AutoField(primary_key=True)
    bom = models.CharField(unique=True, max_length=255)
    description = models.TextField(help_text="e.g. 3G11T 36kW 1500RPM RC 24V IRS")
    model = models.CharField(max_length=20)
    type = models.CharField(max_length=20, help_text="Hint :- mention CRDI, Mechanical, NA, HE")
    series = models.CharField(max_length=20)
class EngResultHeader(models.Model):
    result_id = models.CharField(max_length=100, unique=True)
    esn = models.CharField(max_length=50)
    stno = models.IntegerField()
    # timestamp = models.DateTimeField()
    timestamp = models.DateTimeField(default=timezone.now)  # Automatically handles timezone
    emp_id = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    remark = models.TextField()
    bom_srno = models.ForeignKey(BomList, on_delete=models.CASCADE, related_name='engresultheaders')
class EngResultImages(models.Model):
    result = models.ForeignKey(EngResultHeader, models.DO_NOTHING, to_field='result_id')
    image_id = models.TextField(unique=True)
    directory = models.TextField()
class EngResultAudit(models.Model):
    result_id = models.CharField(unique=True, max_length=50)
    esn = models.CharField(max_length=25)
    stno = models.IntegerField()
    timestamp = models.DateTimeField()
    emp_id = models.IntegerField()
    username = models.CharField(max_length=25)
    remark = models.TextField()
class EngLocation(models.Model):
    id = models.BigAutoField(primary_key=True)
    esn = models.CharField(unique=True, max_length=50)
    bom = models.CharField(max_length=50)
    insp_type = models.BooleanField(blank=True, null=True)
    for_conversion = models.BooleanField(blank=True, null=True)
    cur_loc = models.IntegerField()
    st01_status = models.BooleanField()
    st01_date = models.DateTimeField()
    st02_status = models.BooleanField(blank=True, null=True)
    st02_date = models.DateTimeField(blank=True, null=True)
    st05_status = models.BooleanField(blank=True, null=True)
    st05_date = models.DateTimeField(blank=True, null=True)
    st10_status = models.BooleanField(blank=True, null=True)
    st10_date = models.DateTimeField(blank=True, null=True)
    st12_status = models.BooleanField(blank=True, null=True)
    st12_date = models.DateTimeField(blank=True, null=True)
    st14_status = models.BooleanField(blank=True, null=True)
    st14_date = models.DateTimeField(blank=True, null=True)
    st20_status = models.BooleanField(blank=True, null=True)
    st20_date = models.DateTimeField(blank=True, null=True)
    st22_status = models.BooleanField(blank=True, null=True)
    st22_date = models.DateTimeField(blank=True, null=True)
    st24_status = models.BooleanField(blank=True, null=True)
    st24_date = models.DateTimeField(blank=True, null=True)
    st30_status = models.BooleanField(blank=True, null=True)
    st30_date = models.DateTimeField(blank=True, null=True)
    st32_status = models.BooleanField(blank=True, null=True)
    st32_date = models.DateTimeField(blank=True, null=True)
    st35_status = models.BooleanField(blank=True, null=True)
    st35_date = models.DateTimeField(blank=True, null=True)
    st40_status = models.BooleanField(blank=True, null=True)
    st40_date = models.DateTimeField(blank=True, null=True)
    st42_status = models.BooleanField(blank=True, null=True)
    st42_date = models.DateTimeField(blank=True, null=True)
    st50_status = models.BooleanField(blank=True, null=True)
    st50_date = models.DateTimeField(blank=True, null=True)

    # class Meta:
    #     managed = False
    #     db_table = 'ATP_englocation'
class Locations(models.Model):
    id = models.BigAutoField(primary_key=True)
    loc_id = models.IntegerField()
    location_desc = models.CharField(max_length=40)
    activity = models.CharField(max_length=20)
    pass_field = models.IntegerField(db_column='pass')  # Field renamed because it was a Python reserved word.
    fail = models.IntegerField()
    result_field = models.IntegerField()
class EngResultRework(models.Model):
    result_id = models.CharField(unique=True, max_length=50)
    esn = models.CharField(max_length=25)
    stno = models.IntegerField()
    timestamp = models.DateTimeField()
    emp_id = models.IntegerField()
    username = models.CharField(max_length=25)
    remark = models.TextField()
class EngineAsslyOp(models.Model):
    # id = models.BigAutoField(primary_key=True)
    # esn = models.CharField(max_length=255)
    # crankcase_no = models.CharField(max_length=255)
    # fip_no = models.CharField(max_length=255)
    # turbo_no = models.CharField(max_length=255)
    # #rating = models.CharField(max_length=255)
    # remark = models.CharField(max_length=255, blank=True, null=True)
    # operator_id = models.CharField(max_length=255)
    # timestamp = models.DateTimeField()
    # bom = models.ForeignKey(BomList, on_delete=models.CASCADE, related_name='engineasslyop')
    # status = models.BooleanField()
    # hold_remark = models.CharField(max_length=255, blank=True, null=True)
    # hold_status = models.BooleanField()

    id = models.BigAutoField(primary_key=True)
    esn = models.CharField(max_length=50)
    crankcase_no = models.CharField(max_length=50, blank=True, null=True)
    fip_no = models.CharField(max_length=50, blank=True, null=True)
    turbo_no = models.CharField(max_length=50, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    operator_id = models.CharField(max_length=50, blank=True, null=True)
    bom = models.ForeignKey(BomList, on_delete=models.CASCADE, related_name='engineasslyop')
    timestamp = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    hold_status = models.BooleanField(blank=True, null=True)
    hold_remark = models.CharField(blank=True, null=True)
    timestamp_h = models.DateTimeField(blank=True, null=True)
    operator_h_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'ATP_engineasslyop'


