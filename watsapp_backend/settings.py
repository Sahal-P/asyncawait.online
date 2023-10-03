from pathlib import Path
import os
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = ["localhost", "api.asyncawait.dev","asyncawait.dev", "127.0.0.1"]

INTERNAL_IPS = [
    "127.0.0.1",
]

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    # "debug_toolbar",
    "account",
    "chat",
    "authenticate",
    "notification",
    "storages"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# DEBUG_TOOLBAR_CONFIG = {
#     "SHOW_TOOLBAR_CALLBACK": lambda request: True,
# }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(config("REDIS_HOST"), config("REDIS_PORT", cast=int))],
        },
    },
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "EXCEPTION_HANDLER": "watsapp_backend.exceptions.status_code_handler",
}

ROOT_URLCONF = "watsapp_backend.urls"

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
            ],
        },
    },
]

ASGI_APPLICATION = "watsapp_backend.asgi.application"
WSGI_APPLICATION = "watsapp_backend.wsgi.application"



DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DATABASE_NAME"),
        "USER": config("DATABASE_USER"),
        "PASSWORD": config("DATABASE_PASSWORD"),
        "HOST": config("DATABASE_HOST"),
        # "HOST": config("DATABASE_HOST"),
        "PORT": config("DATABASE_PORT"),
    }
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_CACHE_LOCATION"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHE_TTL = 60 * 1

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': 'db.sqlite3',                      # Or path to database file if using sqlite3.
#         'USER': '',                      # Not used with sqlite3.
#         'PASSWORD': '',                  # Not used with sqlite3.
#         'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#         'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "account.User"

LANGUAGE_CODE = "en-us"

TIME_ZONE = config("TIME_ZONE")

USE_I18N = True

USE_TZ = True


STATIC_URL = config("STATIC_URL")
MEDIA_ROOT = os.path.join(BASE_DIR, config("MEDIA_ROOT"))
MEDIA_URL = config("MEDIA_URL")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    config("CORS_ORIGIN_WHITELIST_1"),
    config("CORS_ORIGIN_WHITELIST_2"),
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOWED_ORIGINS = [
    config("CORS_ALLOWED_ORIGINS_1"),
    config("CORS_ALLOWED_ORIGINS_2"),
]

CORS_ALLOW_HEADERS = [
    "Content-Type",
    "X-User-Identifier",
    "Authorization",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CELERY_BROKER_URL = config("CELERY_BROKER_URL")
# CELERY_BROKER_URL = "amqp://guest:guest@rabbitmq:5672/"
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")

# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SESSION_COOKIE_DOMAIN = 'https://api.asyncawait.dev'

USE_S3=config("USE_S3", cast=bool)

if USE_S3:
    pass
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "()": "colorlog.ColoredFormatter",
            "format": "[%(log_color)s%(levelname)s%(reset)s] %(asctime)s [%(name)s %(funcName)s %(lineno)d] [%(log_color)s%(message)s%(reset)s]",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            "secondary_log_colors": {
                "message": {
                    "DEBUG": "blue",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                }
            },
        },
        "simple": {"format": "[%(levelname)s] %(message)s"},
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            'filters': ['require_debug_true'],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
