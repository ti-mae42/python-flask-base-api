# -*- coding: utf-8 -*-


class InvalidDomain(Exception):
    pass


class NotExist(Exception):
    pass


class RepositoryError(Exception):
    pass


class AlreadyExist(Exception):
    pass


class InvalidEntityData(Exception):
    pass


class EntityNotExist(Exception):
    pass


class EntityAlreadyExist(Exception):
    pass


class CouldNotDelete(Exception):
    pass


class ConfigClassNotFound(Exception):
    pass


class CloudInvalidClientType(Exception):
    pass
