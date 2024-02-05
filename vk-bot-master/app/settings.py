import os

DB_URL = os.getenv("DB_NAME")

CORE_URL = os.getenv("CORE_URL")
CORE_API_URL = CORE_URL + os.getenv("CORE_API_URL")

VK_TOKEN = os.getenv("VK_TOKEN")
VK_TOKEN_CONFIRMATION = os.getenv("VK_TOKEN_CONFIRMATION")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")

SENTRY_URL = os.getenv("SENTRY_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")

CORE_AUTH_TOKEN = os.getenv("AUTH_TOKEN", "ksjdbfksdjbfkjsbdf")

VK_CONF_ID = 2000000000
