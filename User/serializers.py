# serialzer.py
from rest_framework import serializers
from .models import Users, Department, Role, Control
from django.contrib.auth import authenticate, login
from rest_framework.exceptions import AuthenticationFailed




class UserslistSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department__department')
    role = serializers.CharField(source='role__role_name')
    control = serializers.CharField(source='control__control')

    class Meta:
        model = Users
        fields = ['name', 'emp_id', 'username', 'date_joined', 'email', 'is_staff', 'department', 'role', 'control']


class UserslistSerializer2(serializers.ModelSerializer):

    department = serializers.SlugRelatedField(
        queryset=Department.objects.all(),
        slug_field='department'  # Ensure this matches the field in Department model
    )
    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field='role_name'  # Ensure this matches the field in Role model
    )
    control = serializers.SlugRelatedField(
        queryset=Control.objects.all(),
        slug_field='control'  # Ensure this matches the field in Control model
    )

    class Meta:
        model = Users
        fields = ['name', 'emp_id', 'username', 'password', 'date_joined', 'email', 'is_staff', 'department', 'role', 'control']

class UsersSerializer4(serializers.ModelSerializer):
    department = serializers.CharField(source='department__department')
    role = serializers.CharField(source='role__role_name')
    control = serializers.CharField(source='control__control')

    class Meta:
        model = Users
        fields = ['name', 'emp_id', 'username', 'date_joined', 'email', 'is_staff', 'department', 'role', 'control']


class UsersSerializer3(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['name', 'emp_id', 'username', 'password', 'date_joined', 'email', 'is_staff', 'department', 'role', 'control']
        extra_kwargs = {'password': {'write_only': True}}  # Hide password field in response


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['department', 'plant']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_name']

class ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Control
        fields = ['control', 'explain_control']
