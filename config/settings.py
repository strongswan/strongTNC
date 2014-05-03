# -*- coding: utf-8 -*-
# Django settings for strongTNC
import os

try:
    from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
except ImportError:  # py3
    from configparser import ConfigParser, NoSectionError, NoOptionError

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured


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


DEBUG = config.getboolean('debug', 'DEBUG')
TEMPLATE_DEBUG = config.getboolean('debug', 'TEMPLATE_DEBUG')
DEBUG_TOOLBAR = config.getboolean('debug', 'DEBUG_TOOLBAR')

if DEBUG:
    ADMINS = tuple()
else:
    ADMINS = tuple(config.items('admins'))

MANAGERS = ADMINS

try:
    ALLOWED_HOSTS = list(config.items('allowed hosts'))
except (NoSectionError, NoOptionError):
    ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'ipsec.config.db',
    },

    'meta': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django.db',
    },
}

DATABASE_ROUTERS = ['config.router.DBRouter']

LOGIN_URL = '/login'

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
    TIME_ZONE = None

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
STATIC_ROOT = ''

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
    'dajaxice.finders.DajaxiceFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
try:
    SECRET_KEY = config.get('secrets', 'SECRET_KEY')
except (NoSectionError, NoOptionError):
    if DEBUG:
        SECRET_KEY = 'DEBUGGING-SECRETKEY'
    else:
        raise ImproperlyConfigured('Please set SECRET_KEY in your settings.ini.')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'config.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'dajaxice',

    # Own apps
    'tncapp',
    'apps.auth',
    'apps.swid',
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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# DEBUG TOOLBAR
def show_debug_toolbar(request):
    return DEBUG_TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.show_debug_toolbar',
}
