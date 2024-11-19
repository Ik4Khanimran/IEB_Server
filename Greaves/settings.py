"""
Django settings for Greaves project.

Generated by 'django-admin startproject' using Django 4.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

from django.template.context_processors import static

# from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-euu601s3bu2hdt1s@_%ox-+#l$ps^(im0z)d=3gdukvwqqh_a&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


DATA_UPLOAD_MAX_MEMORY_SIZE = 100485760  # 100 MB



ALLOWED_HOSTS = ['localhost','127.0.0.1', 'localhost:8000',
    'http://10.24.0.104:86',
    'http://10.24.0.104:3000',
    'http://localhost:86','http://localhost:8000''http://localhost:8000','10.24.0.104','10.24.1.234','10.24.3.157', ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', 'corsheaders',
    'rest_framework_simplejwt',
    'User',
    'ATP',
    'Common',
    'Api',
    'Quality',
    'Mailer',
    'MC_shop'
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'Greaves.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Greaves.wsgi.application'

# Allow all origins for development purposes (be cautious with this in production)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',  # React dev server
    'http://localhost:8000',  # Django server
    'http://localhost:86',
    'http://10.24.0.104:86',
    'http://10.24.0.104:3000',
]

CORS_ALLOWED_ORIGINS = [
    'http://10.24.0.104:3000',
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:86',
    'http://10.24.0.104:86',

]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    # ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'IEB1',   # Name of Databse
        'USER': 'postgres', # name of user
        'PASSWORD': 'root',
        'HOST': 'localhost',  # Assuming PostgreSQL is running locally
        'PORT': '5432',  # Default PostgreSQL port
    },
    # 'user': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'USER',   # Name of Databse
    #     'USER': 'postgres', # name of user
    #     'PASSWORD': 'root',
    #     'HOST': 'localhost',  # Assuming PostgreSQL is running locally
    #     'PORT': '5432',  # Default PostgreSQL port
    # },
    #
    # 'atp': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'IEB_ATP',   # Name of Databse
    #     'USER': 'postgres', # name of user
    #     'PASSWORD': 'root',
    #     'HOST': 'localhost',  # Assuming PostgreSQL is running locally
    #     'PORT': '5432',  # Default PostgreSQL port
    # }
}

# DATABASE_ROUTERS = ['Greaves.routers.UserRouter']




#Mailer Settings

# Email configuration
#Mailer Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ik4khanimran@gmail.com'
EMAIL_HOST_PASSWORD = 'uthatrfqhztnlyrc'

# Personal Cred
# EMAIL_HOST_USER = 'rishikeshjadhav21@gmail.com'
# EMAIL_HOST_PASSWORD = 'pioccvzwimojoyss'
#DEFAULT_FROM_EMAIL = 'vr.me1@greavescotton.com'



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CELERY_BEAT_SCHEDULE = {
#     'update-days-left-every-day': {
#         'task': 'your_app.tasks.update_days_left',
#         'schedule': crontab(hour=0, minute=0),  # Runs every day at midnight
#     },
# }
# CELERY_BROKER_URL = 'redis://localhost:6379/0'


# Define the URL path to access media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Define the absolute file system path to the media directory
# MEDIA_ROOT = 'D:/Server_Folders/Madhura_Github/IEB_Server/Greaves/Cal_Report'

# # Paths for storing calibration and traceability certificates
# CAL_CERT_PATH = os.path.join(MEDIA_ROOT, 'Cal_Cert_Path')
# TRACE_CERT_PATH = os.path.join(MEDIA_ROOT, 'Trace_Cert_Path')
