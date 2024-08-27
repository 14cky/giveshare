import os
from pathlib import Path
from decouple import config
import sentry_sdk
from dotenv import load_dotenv
import logging

load_dotenv()

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'give.pipeline.get_username',  # Ensure this matches the actual path
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'give.pipeline.link_to_existing_user',  # Ensure this matches the actual path
    'give.pipeline.update_user_profile',  # Ensure this matches the actual path
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'your_app.pipeline': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


STATIC_URL = 'staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

SECRET_KEY = 'django-insecure-tpkt4nn+!*j&bckjjjkenesserik2007haha!@n!hlw9t2j6idpvd9tx_xsfsvnl3+3)zgznn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['giveshare.net', '51.20.201.164', 'www.giveshare.net','127.0.0.1','ec2-51-20-201-164.eu-north-1.compute.amazonaws.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'channels',
    'give',
    'crispy_forms',
    'django_recaptcha',
    'social_django',
    'background_task',
]

RECAPTCHA_PUBLIC_KEY = '6LfDFhQqAAAAALLuBWSYnB8MV-T0ITupcMulcmTH'
RECAPTCHA_PRIVATE_KEY = '6LfDFhQqAAAAADO3F63hHdNrUhT4ZcxzgmZUcnCq'
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'myproject.middleware.TimezoneMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'social_django.context_processors.backends',
    'social_django.context_processors.login_redirect',
]

CSRF_TRUSTED_ORIGINS = [
	'https://giveshare.net',
]

#WSGI_APPLICATION = 'myproject.wsgi.application'
ASGI_APPLICATION = 'myproject.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'channelsdb',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('0.0.0.0', 6380)],        },
    },
}
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'social_core.backends.google.GoogleOAuth2',
)



#for traking local errors Sentry
sentry_sdk.init(
  dsn="https://e35022cfa4daa28e684d8ae306e8a30d@o4507504680370176.ingest.us.sentry.io/4507504683712512",
  # Set traces_sample_rate to 1.0 to capture 100%
  # of transactions for performance monitoring.
  traces_sample_rate=1.0,
  # Set profiles_sample_rate to 1.0 to profile 100%
  # of sampled transactions.
  # We recommend adjusting this value in production.
  profiles_sample_rate=1.0,
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'
IPINFO_TOKEN = 'your_ipinfo_api_token'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'giveshare18@gmail.com'
EMAIL_HOST_PASSWORD = 'xfhu ppnc ijda lrov'
DEFAULT_FROM_EMAIL = 'no-reply@giveshare.net'
DOMAIN_NAME = 'https://giveshare.net'

SESSION_COOKIE_AGE = 30*24*60*60
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_DOMAIN = 'giveshare.net'
CSRF_COOKIE_NAME = 'csrftoken'

# Set GDAL_LIBRARY_PATH to the correct path for your operating system
if os.name == 'nt':  # Windows
    GDAL_LIBRARY_PATH = r'C:\OSGeo4W\bin\gdal309.dll'
    GEOS_LIBRARY_PATH = r'C:\OSGeo4W\bin\geos_c.dll'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '547457235017-s8l3oktmv7a9vpsb028g48dqiiev6od8.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SITE_ID = 3

