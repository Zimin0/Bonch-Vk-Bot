import logging

from redis import Redis
from redis.exceptions import RedisError

from app.settings import REDIS_DB, REDIS_HOST, REDIS_PORT

_redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
logger = logging.getLogger(__name__)


class Cache:
    @staticmethod
    def _get(key):
        try:
            res = _redis_client.get(key)
        except RedisError as err:
            logger.exception(err)
            raise AttributeError from RedisError
        else:
            if res:
                res = res.decode("UTF-8")
            return res

    @staticmethod
    def _set(key, value, seconds):
        try:
            res = _redis_client.set(key, value, ex=seconds)
        except RedisError as err:
            logger.exception(err)
            raise AttributeError from RedisError
        else:
            return res

    @staticmethod
    def _delete(key):
        try:
            res = _redis_client.delete(key)
        except RedisError as err:
            logger.exception(err)
            raise AttributeError from RedisError
        else:
            return res

    @staticmethod
    def _get_keys(pattern):
        try:
            res = _redis_client.keys(pattern)
        except RedisError as err:
            logger.exception(err)
            raise AttributeError from RedisError
        else:
            return res

    def __getattr__(self, key):
        self._get(key)

    def __setattr__(self, key, value, seconds=None):
        self._set(key, value, seconds)

    @classmethod
    def set(cls, key, value, seconds=None):
        cls._set(key, value, seconds)

    @classmethod
    def get(cls, key):
        return cls._get(key)

    @classmethod
    def delete(cls, key):
        return cls._delete(key)

    @classmethod
    def get_keys(cls, pattern):
        return cls._get_keys(pattern)
