import os
from pathlib import Path

from decouple import Csv, config

REVIEW = 0

DEBUG = config('DEBUG', default=True, cast=bool)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-r6wp_#3p3uc*x6*)xv@x%_9$s@pu%jg$ksd4$#hc4svltfnt#g'
)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost http://127.0.0.1',
    cast=Csv()
)

ROOT_URLCONF = 'foodgram.urls'

WSGI_APPLICATION = 'foodgram.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'django_extensions',
    'colorfield'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
    }
}

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':
        ['rest_framework.authentication.TokenAuthentication', ],

    'DEFAULT_PERMISSION_CLASSES':
        ['rest_framework.permissions.IsAuthenticatedOrReadOnly', ],

    'DEFAULT_FILTER_BACKENDS':
        ['django_filters.rest_framework.DjangoFilterBackend', ],
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'recipe': ('api.permissions.AuthorStaffOrReadOnly,',),
        'recipe_list': ('api.permissions.AuthorStaffOrReadOnly',),
        'user': ('api.permissions.AuthorStaffOrReadOnly',),
        'user_list': ('api.permissions.AuthorStaffOrReadOnly',),
    },
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'user_list': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.UserSerializer',
        'user_create': 'api.serializers.UserSerializer',
    },
}

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / STATIC_URL

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / MEDIA_URL

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PASSWORD_RESET_TIMEOUT = 60 * 60

# for review
if REVIEW:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }
