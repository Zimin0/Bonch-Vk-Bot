import logging

from app.db.utils import BaseListModel, BaseModel, Time
from app.settings import CORE_API_URL

logger = logging.getLogger(__name__)


class Platforms(BaseListModel):
    URL = CORE_API_URL + "users/platforms/"
    CACHING = True
    TTL = Time.MINUTES_5


class Platform(BaseModel):
    URL = CORE_API_URL + "users/platforms/"
    CACHING = True
    TTL = Time.HOURS_24
