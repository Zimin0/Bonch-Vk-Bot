import logging

from app.db.utils import BaseListModel, BaseModel, Time
from app.settings import CORE_API_URL

logger = logging.getLogger(__name__)


class Games(BaseListModel):
    URL = CORE_API_URL + "games/"
    CACHING = True
    TTL = Time.HOURS_24


class Game(BaseModel):
    URL = CORE_API_URL + "games/"
    CACHING = True
    TTL = Time.HOURS_24
