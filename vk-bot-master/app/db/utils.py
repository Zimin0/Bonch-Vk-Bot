import json
import logging
from functools import wraps

from aiohttp.client_exceptions import ClientError, ClientResponseError
from app.settings import CORE_AUTH_TOKEN

from app.db.cache import Cache

logger = logging.getLogger(__name__)


def client_exception_wrapper(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            res = fn(*args, **kwargs)
        except (ClientError, ClientResponseError, json.JSONDecodeError) as err:
            logger.exception(err)
            raise err
        else:
            return res
    return wrapper


class Time:
    SECOND_1 = 1
    MINUTES_1 = 60
    MINUTES_3 = MINUTES_1 * 3
    MINUTES_5 = MINUTES_1 * 5
    MINUTES_15 = MINUTES_1 * 15
    MINUTES_20 = MINUTES_1 * 20
    MINUTES_30 = MINUTES_15 * 2
    MINUTES_45 = MINUTES_15 * 3
    HOURS_1 = MINUTES_1 * 60
    HOURS_6 = HOURS_1 * 6
    HOURS_12 = HOURS_6 * 2
    HOURS_18 = HOURS_6 * 3
    HOURS_24 = HOURS_12 * 2
    HOURS_168 = HOURS_12 * 7
    MONTH = HOURS_24 * 31


class BaseModelMixin:
    URL = None
    TTL = None
    CACHING = False

    def __init__(self, data, cached=True):
        self._update(data)
        if cached:
            self._save_cached()

    def _update(self, data):
        self._data = data

    def _save_cached(self):
        pass

    @property
    def data(self):
        return self._data

    @classmethod
    @client_exception_wrapper
    async def create(cls, session, data):
        async with session.post(
                cls.URL, data=data,
                headers={
                    "Authorization": CORE_AUTH_TOKEN
                }) as response:
            data = await response.json()
            return cls(data)

    @classmethod
    @client_exception_wrapper
    async def delete(cls, session, core_id):
        async with session.delete(
                f"{cls.URL}{core_id}",
                headers={
                    "Authorization": CORE_AUTH_TOKEN
                }) as response:
            data = await response.json()
            return cls(data)

    def __bool__(self):
        return bool(self._data)


class BaseModel(BaseModelMixin):
    def _update(self, data):
        self.__dict__.update(data)
        self._data = data

    def _save_cached(self):
        Cache.set(
            f"{type(self).__name__.lower()}_{self._data.get('id')}",
            json.dumps(self._data),
            seconds=self.TTL,
        )
        return self

    @classmethod
    def _find_cached(cls, core_id):
        data = Cache.get(f"{cls.__name__.lower()}_{core_id}")
        if not data:
            return None
        return cls(json.loads(data))

    @classmethod
    def _del_cached(cls, core_id):
        Cache.delete(f"{cls.__name__.lower()}_{core_id}")

    @classmethod
    @client_exception_wrapper
    async def find_by_id(cls, core_id, session, find_cache=True):
        if find_cache:
            cached = cls._find_cached(core_id)
            if cached:
                return cached
        async with session.get(
                f"{cls.URL}{core_id}/", ssl=False,
                headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            data = await response.json()
            return cls(data)


class BaseListModel(BaseModelMixin):
    def _update(self, data):
        self._data = data

    def _save_cached(self):
        Cache.set(
            f"{type(self).__name__.lower()}",
            json.dumps(self._data),
            seconds=self.TTL,
        )
        return self

    @classmethod
    def _find_cached(cls):
        data = Cache.get(f"{cls.__name__.lower()}")
        if not data:
            return None
        return cls(json.loads(data))

    @classmethod
    @client_exception_wrapper
    async def all(cls, session, params=None):
        cached = cls._find_cached()
        if cached:
            return cached
        async with session.get(
            f"{cls.URL}", params=params, ssl=False,
                headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            data = await response.json()
            return cls(data)
