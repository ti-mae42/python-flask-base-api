# -*- coding: utf-8 -*-

from importlib import import_module

from base_api import classproperty


class Service(object):
    _domain = None

    @classproperty
    def domain(cls):
        if cls._domain is None:
            raise NotImplementedError('Service subclasses must define _domain.')
        return import_module(cls._domain)
