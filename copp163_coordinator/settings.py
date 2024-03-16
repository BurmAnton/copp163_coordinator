import os
from os.path import dirname, join
from pathlib import Path

from django.db import models
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

BASE_DIR = Path(__file__).resolve().parent.parent
LOGIN_URL = '/login/'

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG").lower() in ('true', '1', 't')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS').split(' ')

INTERNAL_IPS = [
    "127.0.0.1",
]

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
CELERY_TIMEZONE = 'Europe/Samara'


INSTALLED_APPS = [
    'coverage',
    'debug_toolbar',
    'field_history',
    'django_admin_listfilter_dropdown',
    'users',
    'regions',
    'citizens',
    'education_centers',
    'federal_empl_program',
    'future_ticket',
    'easy_select2',
    'copp163_coordinator.apps.MyAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mathfilters',
    'django_cleanup.apps.CleanupConfig',
    
]

AUTH_USER_MODEL = 'users.User'
AUTH_GROUP_MODEL = 'users.Group'
AUTH_PERMISSION_MODEL = 'users.Permission'

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'copp163_coordinator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'copp163_coordinator.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASS'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379',
        'OPTIONS': {
            'db': '2',
        }
    }
}

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


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Samara'

USE_I18N = True

USE_TZ = True


STATIC_URL = os.environ.get("STATIC_URL")
STATICFILES_DIRS = [
    BASE_DIR / "static",
   # BASE_DIR / "copp163_coordinator/static",
   # '/var/www/copp163_coordinator/static/',
]

MEDIA_ROOT = BASE_DIR
MEDIA_URL = os.environ.get("MEDIA_URL")

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
FIELD_HISTORY_OBJECT_ID_TYPE = (models.CharField, {'max_length': 100})
