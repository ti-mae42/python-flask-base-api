# -*- coding: utf-8 -*-


class Service(object):
    _domain = None

    @classmethod
    def domain(cls):
        if cls._domain is None:
            raise NotImplementedError('Service subclasses must define _domain.')
        return cls._domain
