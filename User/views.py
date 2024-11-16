from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Users, Department, Role, Control
from .serializers import  UserslistSerializer2, UsersSerializer3, UsersSerializer4, UserslistSerializer, DepartmentSerializer, RoleSerializer, ControlSerializer
from rest_framework import serializers
import bcrypt
from django.db.models import Prefetch
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect, requires_csrf_token
from django.utils.decorators import method_decorator
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from Common.logging_config import setup_logger
import logging
import inspect
from django.contrib.auth import authenticate, login


# @method_decorator(csrf_exempt, name='dispatch')

logger = setup_logger(__name__)

class LoginView(APIView):
    def log_with_context(self, message, level=logging.INFO):
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame).__name__
        func_name = frame.f_code.co_name
        logger.log(level, f"Module: {module} - Function: {func_name} - Message: {message} ")

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        print("login")

        self.log_with_context(f'Logging with {username} at {password}', level=logging.INFO)

        try:
            user = Users.objects.get(username=username)
            self.log_with_context(f'found {username}', level=logging.INFO)
        except Users.DoesNotExist:
            self.log_with_context(f'User does not exist', level=logging.ERROR)
            return Response({'message': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, user.password):
            name = user.name
            role = user.role.role_name if user.role else None
            emp_id = user.emp_id
            self.log_with_context(f'PASSWORD CORRECT{name}', level=logging.INFO)
            # Authentication successful
            csrf_token = get_token(request)
            response_data = {
                'success': True,
                'status': 'success',
                'message': 'Authentication successful.',
                'name': name,  # Directly use user's first_name
                'emp_id': emp_id,
                'role': role,
                'csrfToken' : csrf_token,
                }
            return JsonResponse(response_data, status=status.HTTP_200_OK)
        else:
            # Authentication failed
            return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)

    def post_web_app(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        self.log_with_context(f'Logging with {username} at {password}', level=logging.INFO)

        try:
            user = Users.objects.get(username=username)
            self.log_with_context(f'found {username}', level=logging.INFO)
        except Users.DoesNotExist:
            self.log_with_context(f'User does not exist', level=logging.ERROR)
            return Response({'message': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, user.password):
            name = user.name
            role = user.role.role_name if user.role else None
            emp_id = user.emp_id
            self.log_with_context(f'PASSWORD CORRECT{name}', level=logging.INFO)
            # Authentication successful
            csrf_token = get_token(request)
            data = {
            'role': role,
            'name': name,
            'emp_id': emp_id
            }
            return Response({'status': 'success','data' : data, 'message': 'Authentication successful.', 'csrfToken': csrf_token}, status=status.HTTP_200_OK)
        else:
            # Authentication failed
            self.log_with_context(f'PASSWORD INCORRECT', level=logging.ERROR)
            return Response({'message': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    def post_api(self, request):
        print(12345)
        data = request.data
        username = data.get('username')
        password = data.get('password')

        self.log_with_context(f'Logging with {username} at {password}', level=logging.INFO)

        try:
            user = Users.objects.get(username=username)
            self.log_with_context(f'found {username}', level=logging.INFO)
        except Users.DoesNotExist:
            self.log_with_context(f'User does not exist', level=logging.ERROR)
            return Response({'message': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, user.password):

            response_data = {
                'success': True,
                'message': 'Login successful',
                'name': 'Imran111',  # Directly use user's first_name
                'emp_id': 1037117,
            }
            return JsonResponse(response_data, status=200)
        else:
            # Authentication failed
            return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)


@method_decorator(csrf_protect, name='dispatch')
class UserTable(APIView):
    def get(self, request, format=None):
        dropdown_value = request.query_params.get('dropdownValue')

        if dropdown_value == 'user_list':
            queryset = Users.objects.prefetch_related(
                Prefetch('department_set', queryset=Department.objects),
                Prefetch('role_set', queryset=Role.objects),
                Prefetch('control_set', queryset=Control.objects)
            ).values(
                'name', 'emp_id', 'username', 'date_joined', 'email', 'is_staff',
                'department__department', 'role__role_name', 'control__control'
            )

            serializer = UserslistSerializer(queryset, many=True)
        elif dropdown_value == 'department_list':
            queryset = Department.objects.all()
            serializer = DepartmentSerializer(queryset, many=True)
        elif dropdown_value == 'role_list':
            queryset = Role.objects.all()
            serializer = RoleSerializer(queryset, many=True)
        elif dropdown_value == 'control_list':
            queryset = Control.objects.all()
            serializer = ControlSerializer(queryset, many=True)
        else:
            return Response({'status': 'error', 'message': 'Invalid dropdown value'},
                            status=status.HTTP_400_BAD_REQUEST)
        #  Return the serialized data
        return Response({'status': 'success', 'table_data': serializer.data}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class CreateUserTable(APIView):

    def get(self, request, format=None):
        dropdown_value = request.query_params.get('dropdownValue')

        # Define a mapping of table names to serializers
        serializer_mapping = {
            'role_list': RoleSerializer,
            'control_list': ControlSerializer,
            'user_list': UserslistSerializer2,
            'department_list': DepartmentSerializer,
        }
        serializer_class = serializer_mapping.get(dropdown_value)

        if serializer_class:
            serializer = serializer_class()
            # Get the fields of the serializer
            fields_info = []
            for field_name, field in serializer.fields.items():
                if dropdown_value != 'user_list' and field_name == serializer.Meta.model._meta.pk.name:
                    continue
                field_type = None
                choices = None
                max_length = None

                if isinstance(field, serializers.IntegerField):
                    field_type = 'integer'
                elif isinstance(field, serializers.DateTimeField):
                    field_type = 'datetime'
                elif isinstance(field, serializers.BooleanField):
                    field_type = 'boolean'
                elif isinstance(field, serializers.EmailField):
                    field_type = 'email'
                elif isinstance(field, serializers.RelatedField):
                    field_type = 'foreignkey'
                    related_model = field.queryset.model
                    if field_name == 'department':
                        choices = list(related_model.objects.all().values('dept_id', 'department'))
                    if field_name == 'role':
                        choices = list(related_model.objects.all().values('role_id', 'role_name'))
                    if field_name == 'control':
                        choices = list(related_model.objects.all().values('control_id', 'control'))
                    if field_name == 'department':
                        choices = list(related_model.objects.all().values('dept_id', 'department'))


                elif isinstance(field, serializers.CharField):
                    field_type = 'password' if field_name == 'password' else (
                        'email' if field_name == 'email' else 'text')
                    max_length = getattr(field, 'max_length', None)

                help_text = getattr(serializer.Meta.model, field_name).field.help_text if hasattr(serializer.Meta.model,
                                                                                                  field_name) else None

                fields_info.append({
                    'name': field_name,
                    'type': field_type,
                    'help_text': help_text,
                    'choices': choices,
                    'max_length': max_length
                })

            return Response({'status': 'success', 'fields': fields_info, 'dropdown_value': dropdown_value},
                            status=status.HTTP_200_OK)

        return Response({"error": "Invalid dropdown value"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            tablename = request.data['formTable']['tableName']
            Serializer_mapping = {
                'role_list': RoleSerializer,
                'control_list': ControlSerializer,
                'user_list': UsersSerializer3,
                'department_list': DepartmentSerializer,
            }
            serializersname = Serializer_mapping.get(tablename)
            if not serializersname:
                return Response({"error": "Invalid table name"}, status=status.HTTP_400_BAD_REQUEST)

            user_data = request.data['formData']
            user_serializer = serializersname(data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
                data = {
                    "status": "success",
                    "message": "User created successfully",
                    "values": user_serializer.data
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                data = {
                    "status": "error",
                    "message": user_serializer.errors
                }
                print(data)
                return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, format=None):
        try:
            tablename = request.data['tableName']['dropdown']
            Serializer_mapping = {
                'role_list': RoleSerializer,
                'control_list': ControlSerializer,
                'user_list': UsersSerializer4,
                'department_list': DepartmentSerializer,
            }
            Model_mapping = {
                'role_list': Role,
                'control_list': Control,
                'user_list': Users,
                'department_list': Department,
            }

            serializer_class = Serializer_mapping.get(tablename)
            modelname = Model_mapping.get(tablename)

            if not serializer_class or not modelname:
                print("no model")
                return Response({"error": "Invalid table name"}, status=status.HTTP_400_BAD_REQUEST)

            if tablename == "department_list":
                instance_id = request.data['formData'][
                    'dept_id']  # Assuming you pass the id of the instance to be updated
                instance = modelname.objects.get(dept_id=instance_id)
            if tablename == "control_list":
                instance_id = request.data['formData'][
                    'control_id']  # Assuming you pass the id of the instance to be updated
                instance = modelname.objects.get(control_id=instance_id)
            if tablename == "role_list":
                instance_id = request.data['formData'][
                    'role_id']  # Assuming you pass the id of the instance to be updated
                instance = modelname.objects.get(role_id=instance_id)
            if tablename == "user_list":
                instance_id = request.data['formData'][
                    'username']  # Assuming you pass the id of the instance to be updated
                instance = modelname.objects.get(username=instance_id)

            edit_data = request.data['formData']
            if tablename == "user_list":
                # Update the department field
                if 'department' in edit_data:
                    department_name = edit_data['department']
                    department_instance = Department.objects.get(department=department_name)
                    edit_data['department'] = department_instance.pk  # Assuming department is a ForeignKey
                if 'role' in edit_data:
                    role_name = edit_data['role']
                    role_instance = Role.objects.get(role_name=role_name)
                    edit_data['role'] = role_instance.pk  # Assuming department is a ForeignKey
                if 'control' in edit_data:
                    control_name = edit_data['control']
                    control_instance = Control.objects.get(control=control_name)
                    edit_data['control'] = control_instance.pk  # Assuming department is a ForeignKey

                user_serializer = serializer_class(instance, data=edit_data, partial=True)
            else:
                user_serializer = serializer_class(instance, data=edit_data, partial=True)


            if user_serializer.is_valid():
                user_serializer.save()
                data = {
                    "status": "success",
                    "message": "User updated successfully",
                    "values": user_serializer.data
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {
                    "status": "error",
                    "message": user_serializer.errors
                }
                return Response(data, status=status.HTTP_200_OK)

        except modelname.DoesNotExist:
            print("error")
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("error", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, format=None):
        try:
            tablename = request.data['dropdownValue']
            Model_mapping = {
                'role_list': RoleSerializer,
                'control_list': ControlSerializer,
                'user_list': UsersSerializer3,
                'department_list': DepartmentSerializer,
            }
            serializer_class = Model_mapping.get(tablename)
            print(serializer_class)
            if not serializer_class:
                return Response({"error": "Invalid table name"}, status=status.HTTP_400_BAD_REQUEST)

            if tablename == "department_list":
                model_instance = serializer_class.Meta.model.objects.get(pk=request.data['rowData']['dept_id'])
            if tablename == "control_list":
                model_instance = serializer_class.Meta.model.objects.get(pk=request.data['rowData']['control_id'])
            if tablename == "role_list":
                model_instance = serializer_class.Meta.model.objects.get(pk=request.data['rowData']['role_id'])
            if tablename == "user_list":
                model_instance = serializer_class.Meta.model.objects.get(pk=request.data['rowData']['username'])

            # model_instance.delete()

            data = {
                "status": "success",
                "message": "User deleted successfully"
            }
            return Response(data, status=status.HTTP_200_OK)

        except model_instance.DoesNotExist:
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)