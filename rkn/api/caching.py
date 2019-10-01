"""
Caching immplementation with Redis.
Provides failover, which means no caching
"""
import redis
import pickle

from api.settings import redisconf


connection = redis.Redis(**redisconf.conn)
try:
    connection.ping()
except redis.exceptions.RedisError:
    connection = None


def _getCache(key):
    if not connection:
        return None
    return connection.get(key)


def _setCache(key, value):
    if connection:
        connection.set(key, value, ex=redisconf.ttl)


def getDataCached(func, *args, **kwargs):
    """
    Caching decorator
    :param func: any callable
    :param args: arguments
    :param kwargs: keyword arguments
    :return: cache hit or function result on miss, with caching
    """
    key = pickle.dumps(
            [func, args, kwargs])
    cache = _getCache(key)
    if cache:
        return pickle.loads(cache)

    result = func(*args, **kwargs)
    _setCache(key, pickle.dumps(result))
    return result


def flushCache():
    connection.flushall()
