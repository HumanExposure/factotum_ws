import os

from config.environment import env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = env.DEBUG
SECRET_KEY = env.SECRET_KEY
ALLOWED_HOSTS = env.ALLOWED_HOSTS

THIRD_PARTY_OVERRIDE_APPS = ["whitenoise.runserver_nostatic"]
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = ["dashboard", "django_filters", "rest_framework"]
LOCAL_APPS = ["app.api", "app.docs", "app.core"]
INSTALLED_APPS = THIRD_PARTY_OVERRIDE_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.SQL_DATABASE,
        "USER": env.SQL_USER,
        "PASSWORD": env.SQL_PASSWORD,
        "HOST": env.SQL_HOST,
        "PORT": env.SQL_PORT,
        "TEST": {"NAME": "test_" + env.SQL_DATABASE + "_factotum_ws"},
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "collected_static")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = DEBUG

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "app.core.pagination.StandardPagination",
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "PAGE_SIZE": 100,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "URL_FIELD_NAME": "link",
}

SWAGGER_SETTINGS = {
    "DEFAULT_GENERATOR_CLASS": "app.core.generators.StandardSchemaGenerator",
    "DEFAULT_AUTO_SCHEMA_CLASS": "app.core.inspectors.StandardAutoSchema",
    "DEFAULT_FIELD_INSPECTORS": [
        "drf_yasg.inspectors.CamelCaseJSONFilter",
        "drf_yasg.inspectors.ReferencingSerializerInspector",
        "drf_yasg.inspectors.RelatedFieldInspector",
        "drf_yasg.inspectors.ChoiceFieldInspector",
        "drf_yasg.inspectors.FileFieldInspector",
        "drf_yasg.inspectors.DictFieldInspector",
        "drf_yasg.inspectors.JSONFieldInspector",
        "drf_yasg.inspectors.HiddenFieldInspector",
        "drf_yasg.inspectors.RecursiveFieldInspector",
        "drf_yasg.inspectors.SerializerMethodFieldInspector",
        "drf_yasg.inspectors.SimpleFieldInspector",
        "drf_yasg.inspectors.StringDefaultFieldInspector",
    ],
    "DEFAULT_FILTER_INSPECTORS": ["app.core.inspectors.DjangoFiltersInspector"],
    "DEFAULT_PAGINATOR_INSPECTORS": ["app.core.inspectors.StandardPaginatorInspector"],
    "SECURITY_DEFINITIONS": {},
}

LOGGING = {
    "version": 1,
    "formatters": {
        "console": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "[%d/%b/%Y %H:%M:%S]",
            "class": "logging.Formatter",
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] [INFO] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "logstash": {
            "level": "INFO",
            "class": "logstash.UDPLogstashHandler",
            "host": env.LOGSTASH_HOST,
            "port": int(env.LOGSTASH_PORT),
            "version": 1,
            "message_type": "django",
            "fqdn": False,
            "tags": ["factotum_ws", "access"],
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.server": {
            "handlers": ["logstash", "django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["logstash", "console"],
            "propagate": False,
        },
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
