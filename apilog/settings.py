# Django settings for apilog project.
import os
from django.core.exceptions import ImproperlyConfigured

# Defensive code for improperly configured settings
msg = "Set the {} environment variable"


def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        raise ImproperlyConfigured(msg.format(var_name))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',
        # Or path to database file if using sqlite3.
        'NAME': 'database.sql',
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'HOST': '',
        # Set to empty string for default.
        'PORT': '',
    }
}

# Mongodb connection data
MONGODB = {
    'hosts': ['localhost:27017', ],
    'dbname': "logs",
    'operation_ack': 0,
    'slave_ok': True,
    'replicaset': '',
    'autostart': True
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

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
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = get_env_variable("SECRET")

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'log_request_id.middleware.RequestIDMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'apilog.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'apilog.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    'django_nose',
    # Own apps
    'rest_framework',
    'api',
)

# Nosetests settings
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Logger configuration
LOGGING_ROOT = os.path.abspath('/opt/bvp/log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'DEBUG',
        'handlers': ['debug', 'all']
    },
    'formatters': {
        'verbose': {
            'format': '%(request_id)s | %(asctime)s | %(machine)s | %(module)s | %(levelname)s | %(request_id)s | '
                      'apilog | %(module)s | %(process)d | %(thread)d | %(message)s'
        },
        'simple': {
            'format': '%(request_id)s | %(asctime)s | %(module)s | %(levelname)s | apilog | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'filters': {
        'log_filter': {
            '()': 'apilog.filterhelper.AddMachineFilter'},
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'}
    },
    'handlers': {
        'parser': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': os.path.join(LOGGING_ROOT, "py.apilog.parser" + '.log')
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['log_filter', 'request_id'],
            'formatter': 'simple',
            'filename': os.path.join(LOGGING_ROOT, "py.apilog.debug" + '.log'),
        },
        'all': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filters': ['request_id'],
            'formatter': 'verbose',
            'filename': os.path.join(LOGGING_ROOT, "py.apilog.all" + '.log')}
    },
    'loggers': {
        'apilog': {
            'handlers': ['debug'],
            'level': 'INFO',
            'propagate': True
        },
        'apilog.parser': {
            'handlers': ['parser'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
