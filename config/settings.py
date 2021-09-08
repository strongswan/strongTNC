# -*- coding: utf-8 -*-
# Django settings for strongTNC
import os

try:
    from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
except ImportError:  # py3
    from configparser import RawConfigParser, NoSectionError, NoOptionError

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured

import dj_database_url


# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Read configuration from ini
config = RawConfigParser()
if os.path.exists('config/settings.ini'):
    config.read('config/settings.ini')
elif os.path.exists('/etc/strongTNC/settings.ini'):
    config.read('/etc/strongTNC/settings.ini')
else:
    raise ImproperlyConfigured('No settings.ini found. Please copy `config/settings.sample.ini` ' +
            'to either `config/settings.ini` or `/etc/strongTNC/settings.ini` and configure it ' +
            'to your likings.')


# Debug variables
DEBUG = config.getboolean('debug', 'DEBUG')
TEMPLATE_DEBUG = config.getboolean('debug', 'TEMPLATE_DEBUG')
DEBUG_TOOLBAR = config.getboolean('debug', 'DEBUG_TOOLBAR')

# Admins and managers
if DEBUG:
    ADMINS = tuple()
else:
    ADMINS = tuple(config.items('admins'))
MANAGERS = ADMINS

# Allowed hosts (only used in production)
try:
    _allowed_hosts = config.get('security', 'ALLOWED_HOSTS')
    ALLOWED_HOSTS = [x for x in _allowed_hosts.replace(' ', '').split(',') if x]
except (NoSectionError, NoOptionError):
    ALLOWED_HOSTS = []

# Security
try:
    CSRF_COOKIE_SECURE = config.getboolean('security', 'CSRF_COOKIE_SECURE')
except (NoSectionError, NoOptionError):
    CSRF_COOKIE_SECURE = False

# Database configuration
DATABASES = {}
try:
    DATABASES['default'] = dj_database_url.parse(config.get('db', 'STRONGTNC_DB_URL'))
except (NoSectionError, NoOptionError):
    kwargs = {'env': 'STRONGTNC_DB_URL', 'default': 'sqlite:///ipsec.config.db'}
    DATABASES['default'] = dj_database_url.config(**kwargs)
try:
    DATABASES['meta'] = dj_database_url.parse(config.get('db', 'DJANGO_DB_URL'))
except (NoSectionError, NoOptionError):
    kwargs = {'env': 'DJANGO_DB_URL', 'default': 'sqlite:///django.db'}
    DATABASES['meta'] = dj_database_url.config(**kwargs)
DATABASE_ROUTERS = ['config.router.DBRouter']

# Auth URLs
LOGIN_URL = '/login'

# XMPP configuration
XMPP_GRID = {}
try:
    USE_XMPP = config.getboolean('xmpp', 'USE_XMPP')
    XMPP_GRID['jid'] = config.get('xmpp', 'jid')
    XMPP_GRID['password'] = config.get('xmpp', 'password')
    XMPP_GRID['pubsub_server'] = config.get('xmpp', 'pubsub_server')
    XMPP_GRID['cacert'] = config.get('xmpp', 'cacert')
    XMPP_GRID['certfile'] = config.get('xmpp', 'certfile')
    XMPP_GRID['keyfile'] = config.get('xmpp', 'keyfile')
    XMPP_GRID['use_ipv6'] = config.getboolean('xmpp', 'use_ipv6')
    XMPP_GRID['node_swidtags'] = config.get('xmpp', 'node_swidtags')
    XMPP_GRID['node_events'] = config.get('xmpp', 'node_events')
    XMPP_GRID['rest_uri'] = config.get('xmpp', 'rest_uri')

except (NoSectionError, NoOptionError):
    USE_XMPP = False


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
USE_TZ = True
try:
    TIME_ZONE = config.get('localization', 'TIME_ZONE')
except (NoSectionError, NoOptionError):
    TIME_ZONE = 'UTC'

DEFAULT_DATETIME_FORMAT_STRING = '%b %d %H:%M:%S %Y'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
try:
    LANGUAGE_CODE = config.get('localization', 'LANGUAGE_CODE')
except (NoSectionError, NoOptionError):
    LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
try:
    _static_root = config.get('paths', 'STATIC_ROOT')
    if _static_root.startswith('/'):
        STATIC_ROOT = _static_root
    else:
        STATIC_ROOT = os.path.join(PROJECT_ROOT, _static_root)
except (NoSectionError, NoOptionError):
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
try:
    SECRET_KEY = config.get('security', 'SECRET_KEY')
except (NoSectionError, NoOptionError):
    if DEBUG:
        SECRET_KEY = 'DEBUGGING-SECRETKEY' # noqa
    else:
        raise ImproperlyConfigured('Please set SECRET_KEY in your settings.ini.')

# List of callables that know how to import templates from various sources.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.version',
            ],
        },
    },
]

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
if DEBUG_TOOLBAR:
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'config.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django_filters',
    'rest_framework',

    # Own apps
    'apps.front',
    'apps.core',
    'apps.authentication',
    'apps.policies',
    'apps.devices',
    'apps.packages',
    'apps.filesystem',
    'apps.swid',
    'apps.tpm',
    'apps.api',
)
if DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
try:
    if config.getboolean('debug', 'SQL_DEBUG'):
        # This will cause all SQL queries to be printed
        LOGGING['loggers']['django.db.backends'] = {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
except (NoSectionError, NoOptionError):
    pass

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# DEBUG TOOLBAR
def show_debug_toolbar(request):
    return DEBUG_TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.show_debug_toolbar',
}


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        'rest_framework.parsers.FormParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'apps.authentication.permissions.IsStaffOrHasWritePerm',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.HyperlinkedModelSerializer',
    'URL_FIELD_NAME': 'uri',
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
