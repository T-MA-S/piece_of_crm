import os
from pathlib import Path

import environ
from django.utils.translation import gettext_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(env('DEBUG')))

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    'django_prometheus',
    'storages',
    'django_crontab',

    'captcha',
    'phonenumber_field',

    'users.apps.UsersConfig',
    'refferal.apps.RefferalConfig',
    'dashboard.apps.DashboardConfig',
    'company.apps.CompanyConfig',
    'crm.apps.CrmConfig',
    'payment.apps.PaymentConfig',
    'logger.apps.LoggerConfig',

    'django.contrib.sites.apps.SitesConfig',
    'django.contrib.humanize.apps.HumanizeConfig',
    'django_nyt.apps.DjangoNytConfig',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'wiki.apps.WikiConfig',
    'wiki.plugins.attachments.apps.AttachmentsConfig',
    'wiki.plugins.notifications.apps.NotificationsConfig',
    'wiki.plugins.images.apps.ImagesConfig',
    'wiki.plugins.macros.apps.MacrosConfig',

]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'logger.middleware.LoggingMiddleware',

    'users.middlewares.login_required.UserLoginRequiredMiddleware',

    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'SalesTech.urls'

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
                'sekizai.context_processors.sekizai'
            ],
        },
    },
]

WSGI_APPLICATION = 'SalesTech.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DB_TYPE = env('DB_TYPE')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env(f'{DB_TYPE}_DATABASE_NAME'),
        'USER': env(f'{DB_TYPE}_DATABASE_USER'),
        'PASSWORD': env(f'{DB_TYPE}_DATABASE_PASS'),
        'HOST': env(f'{DB_TYPE}_DATABASE_HOST'),
        'PORT': env(f'{DB_TYPE}_DATABASE_PORT')
    },
    "logger": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env(f'{DB_TYPE}_LOGGER_DATABASE_NAME'),
        "USER": env(f'{DB_TYPE}_LOGGER_DATABASE_USER'),
        "PASSWORD": env(f'{DB_TYPE}_LOGGER_DATABASE_PASS'),
        "HOST": env(f'{DB_TYPE}_LOGGER_DATABASE_HOST'),
        "PORT": env(f'{DB_TYPE}_LOGGER_DATABASE_PORT')
    }
}

AUTH_USER_MODEL = "users.UserModel"

# Password validation


# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

LOGIN_URL = '/ru/users/login/'

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LANGUAGES = (
    ('ru', gettext_lazy('Russian')),
    ('en', gettext_lazy('English')),

)

LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'SalesTech/static',
]

STATIC_ROOT = 'static'

MEDIA_ROOT = '/media/'

EMAIL_USE_TLS = True
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT')

MILLIONVERIFIER_API_KEY = env('MILLIONVERIFIER_API_KEY')

ROBOKASSA_MERCHANT_LOGIN = env('ROBOKASSA_MERCHANT_LOGIN')
ROBOKASSA_MERCHANT_PASSWORD_1 = env(f'ROBOKASSA_PASSWORD_{DB_TYPE}_1')
ROBOKASSA_MERCHANT_PASSWORD_2 = env(f'ROBOKASSA_PASSWORD_{DB_TYPE}_2')
ROBOKASSA_ISTEST = int(env(f'ROBOKASSA_{DB_TYPE}'))

# S3 settings
AWS_S3_ENDPOINT_URL = 'https://storage.yandexcloud.net'
AWS_S3_ACCESS_KEY_ID = os.getenv(f'{DB_TYPE}_AWS_S3_ACCESS_KEY_ID')
AWS_S3_SECRET_ACCESS_KEY = os.getenv(f'{DB_TYPE}_AWS_S3_SECRET_ACCESS_KEY')
AWS_QUERYSTRING_AUTH = True

USER_UPLOADED_FILES_DIRECTORY_IN_BUCKET = 'user_upload_files/'
AVATAR_FILE_DIRECTORY_IN_BUCKET = f'{USER_UPLOADED_FILES_DIRECTORY_IN_BUCKET}avatars/'
CONTRACTS_FILE_DIRECTORY_IN_BUCKET = f'{USER_UPLOADED_FILES_DIRECTORY_IN_BUCKET}contracts/'
BUCKET_NAME = os.getenv('BUCKET_NAME')

DEFAULT_FILE_STORAGE = 'SalesTech.s3_storage.MediaStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PHONENUMBER_DEFAULT_REGION = "RU"

MODELTRANSLATION_LANGUAGES = ('en', 'ru')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'console': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'file': {
            'format': '%(asctime).19s %(levelname)s - %(user_ip)s %(user_email)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'console'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'debug.log',
            'encoding': 'utf8',
        }
    },
    'loggers': {
        'py.warnings': {
            'level': 'DEBUG',
            'handlers': ['console', ],
        },
        'user_events': {
            'level': 'INFO',
            'handlers': ['file']
        }
    }
}

DATABASE_ROUTERS = ['logger.dbrouters.DbRouter', ]
SITE_ID = 1
WIKI_ACCOUNT_HANDLING = False

VERIFIER_URL = "http://mail-v.salestech.pro"

TELEGRAM_BOT_API_KEY = os.getenv('TELEGRAM_BOT_API_KEY')
TELEGRAM_CHAT = os.getenv('TELEGRAM_CHAT')


CRONJOBS = [
    ('*/1 * * * *', 'company.cron_jobs.start_sending_mails'),
    ('*/10 * * * *', 'company.cron_jobs.start_rateplan_checker')
]

if not DEBUG:
    CRONJOBS.append(
        ('0 */6 * * *', 'company.cron_jobs.start_email_checker')
    )

