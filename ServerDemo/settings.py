"""
Django settings for ServerDemo project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*%oh90*#+*b(exl!bd098kk)*t%rxfm$gov)t!axjoh-=+)47l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
DOMAIN = ('localhost:8000')
SITE_NAME = ('CourseDog')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

########## SEND GRID EMAIL CONFIGURATION ###########
SENDGRID_API_KEY = "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"

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'  # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = "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"

EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'beatzcf2014@gmail.com'
ADMINS = [('Omar Khaled', 'beatzcf2014@gmail.com')]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://localhost:3000'
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'https://localhost:3000'
]
CORS_ORIGIN_WHITELIST = ['http://localhost:3000',
                         'https://localhost:3000']
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    'access-control-allow-origin',
    'access-control-allow-headers',
    'access-control-allow-methods',
    'access-control-allow-credentials',
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_extensions',
    'djoser',
    'authentication',
    'course',
    'material',
    'announcement',
    'organization',
    'user_profile',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_celery_results',
    'django_cron'
]

CRON_CLASSES = [
    'ServerDemo.crons.MyCronJob'
]

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

SITE_ID = 1
LOGIN_REDIRECT_URL = '/user-profile/check/'

LOGOUT_REDIRECT_URL = '/user-profile/logged-out/'

ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGOUT_REDIRECT_URL = LOGOUT_REDIRECT_URL
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        "SCOPE": [
            'profile',
            'email',
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/classroom.courses",
            "https://www.googleapis.com/auth/classroom.announcements.readonly",
            "https://www.googleapis.com/auth/classroom.courses.readonly",
            "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly"
        ],
        "AUTH_PARAMS": {
            "access_type": "offline",
        },
        "METHOD": "oauth2", # 'oauth2' or 'oauth'
        'OAUTH_PKCE_ENABLED': True,
    },
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DJOSER = {
    'LOGIN_FIELD': 'email',
    "USER_ID_FIELD": "username",
    'ACTIVATION_URL': 'auth/activate-user/{uid}/{token}/',
    'SEND_ACTIVATION_EMAIL': True,
    'PASSWORD_RESET_CONFIRM_URL': 'auth/reset/password/{uid}/{token}/',
    'SERIALIZERS': {
        'user_create': 'authentication.serializers.UserRegistrationSerializer',
    },
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 4,
}
ROOT_URLCONF = 'ServerDemo.urls'

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

WSGI_APPLICATION = 'ServerDemo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'course-dog-db',
        'USER': 'course-dog',
        'PASSWORD': '1010abab',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = BASE_DIR / 'uploads/'
MEDIA_URL = '/files/'
