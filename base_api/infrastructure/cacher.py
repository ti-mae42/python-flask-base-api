# -*- coding: utf-8 -*-

import redis


class CacherClient(object):
    def __init__(self, redis_url=None, testing=False):
        self._client = None
        if testing:
            return
        if redis_url:
            self._client = redis.Redis.from_url(redis_url)


class ExpiringKeyStore(CacherClient):
    _keys_on_test = {}

    def set_once(self, key, value, expiration_seconds):
        if self._client is None:
            if key in self._keys_on_test:
                return False
            self._keys_on_test[key] = value
            return True
        return self._client.set(key, value, nx=True, ex=expiration_seconds)

    @classmethod
    def reset_keys_on_test(cls):
        cls._keys_on_test = {}
