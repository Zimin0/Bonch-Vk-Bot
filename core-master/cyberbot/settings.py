import os
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!


SECRET_KEY = os.getenv("SECRET_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not ENVIRONMENT in ("production", "staging")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_celery_beat",
    "django_filters",
    "users",
    "teams",
    "tournaments",
    "games",
    "steam_auth",
    "battlenet_auth"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cyberbot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "cyberbot.wsgi.application"

# Database


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# Password validation


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{name}"}
    for name in [
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    ]
]

# Internationalization


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Sentry
# pylint: disable=abstract-class-instantiated
sentry_sdk.init(
    dsn=os.getenv("SENTRY_URL"),
    environment=ENVIRONMENT,
    integrations=[
        LoggingIntegration(),
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True,
)

# Static files (CSS, JavaScript, Images)


STATIC_URL = "/static/"
STATIC_ROOT = os.getcwd() + "/static/"

# Default primary key field type


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": ("users.backends.JWTAuthentication",),
}

APPEND_SLASH = True

# Celery Configuration Options
CELERY_BROKER_URL = os.getenv("REDIS_URL")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CLASH_ROYALE_API_TOKEN = os.getenv("CLASH_ROYALE_API_TOKEN")

VK_BOT_URL = os.getenv("VK_BOT_URL")

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000


AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.steam.SteamOpenId',
    'django.contrib.auth.backends.ModelBackend',
)

STEAM_KEY = os.getenv("STEAM_KEY")
STEAM_URL = os.getenv("STEAM_URL")

BNET_KEY = os.getenv("BNET_KEY")
BNET_SECRET = os.getenv("BNET_SECRET")
BNET_REDIRECT_URI = os.getenv("BNET_REDIRECT_URI")


AUTH_TOKEN = os.getenv("AUTH_TOKEN", "ksjdbfksdjbfkjsbdf")
