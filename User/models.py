# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.hashers import make_password
import re

from django.db import models

# Create your models here.

class Control(models.Model):
    control_id = models.AutoField(primary_key=True)
    control = models.CharField(max_length=20, help_text="Create a new control e.g superuser, Admin, Auditor, Operator")
    explain_control = models.TextField(
        help_text="Explain what actions they can perform e.g. Edit, delete, Atp, M/c Shop")


class Department(models.Model):
    dept_id = models.AutoField(primary_key=True)
    department = models.CharField(max_length=30, help_text="Create new department, e.g. ME, Quality")
    plant = models.CharField(max_length=20, help_text="Create new Plant, e.g. 1170, 1130")


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=30, help_text="create new role e.g. Operator, Supervisior, HOD, Manager")


class Users(models.Model):
    name = models.CharField(max_length=20)
    emp_id = models.IntegerField()
    username = models.CharField(primary_key=True, max_length=20)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(blank=True, null=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField()
    department = models.ForeignKey(Department, models.DO_NOTHING, db_column='department', blank=True, null=True)
    role = models.ForeignKey(Role, models.DO_NOTHING, db_column='role', blank=True, null=True)
    control = models.ForeignKey(Control, models.DO_NOTHING, db_column='control', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)  # Hash password before saving
        return super().save(*args, **kwargs)
