import logging

from app.db import Cache
from app.db.models import core
from app.db.utils import BaseModel, Time, client_exception_wrapper
from app.settings import CORE_API_URL, CORE_AUTH_TOKEN

logger = logging.getLogger(__name__)


class Csgo(BaseModel):
    URL = CORE_API_URL + "tournaments/csgo/"
    CACHING = True
    TTL = Time.MINUTES_1

    @classmethod
    @client_exception_wrapper
    async def get_peak_stages(cls, session, match_id):
        async with session.get(
                f"{cls.URL}peak/queue/{match_id}/", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            matches = await response.json()
            return matches

    @classmethod
    @client_exception_wrapper
    async def get_maps(cls, session):
        async with session.get(
                f"{cls.URL}maps", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            maps = await response.json()
            return maps

    @classmethod
    @client_exception_wrapper
    async def create_peak(cls, session, data):
        async with session.post(
                f"{cls.URL}peak/", headers={
                    "Authorization": CORE_AUTH_TOKEN
                },
                data=data,
        ) as response:
            peak = await response.json()
            return peak
