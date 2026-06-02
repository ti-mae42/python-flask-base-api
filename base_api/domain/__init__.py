# -*- coding: utf-8 -*-

from base_api import exceptions


class Entity(object):
    repository = None

    @staticmethod
    def _is_unique_violation(exception):
        message = str(exception).lower()
        markers = [
            'duplicate key value violates unique',
            'unique constraint failed',
            'duplicate entry',
        ]
        return any(marker in message for marker in markers)

    @classmethod
    def list_all(cls):
        return [cls.create_with_instance(instance) for instance in cls.repository.list_all()]

    @classmethod
    def list_with_filter(cls, **filter_params):
        return [cls.create_with_instance(instance) for instance in cls.repository.list_with_filter(**filter_params)]

    @classmethod
    def list_with_filter_and_paginate(cls, page, page_size, **filter_params):
        items, total = cls.repository.list_with_filter_and_paginate(page, page_size, **filter_params)
        return [cls.create_with_instance(instance) for instance in items], total

    @classmethod
    def create_new(cls, json_data, user_id=None):
        try:
            return cls(cls.repository.create_from_json(json_data, user_id=user_id))
        except exceptions.RepositoryError as ex:
            if cls._is_unique_violation(ex):
                raise exceptions.AlreadyExist(f'Entity with {json_data} already exists in repository')
            raise

    @classmethod
    def create_with_id(cls, entity_id):
        instance = cls.repository.get(entity_id)
        return cls.create_with_instance(instance)

    @classmethod
    def create_with_instance(cls, instance):
        if instance is None:
            raise exceptions.NotExist('Tried to create entity with instance None. Check the call stack.')
        return cls(instance)

    def __init__(self, instance=None):
        self.instance = instance
        self.id = None
        if instance is not None:
            self.id = instance.id

    def save(self, user_id=None):
        self.instance.save_db(user_id=user_id)

    def update_me(self, json_data, user_id=None):
        self.instance.update_from_json(json_data, user_id=user_id)

    def delete_me(self, user_id=None):
        self.instance.delete_db(user_id=user_id)

    def as_dict(self, compact=False):
        return {'id': self.id}


class ValueEntity(Entity):
    repository = None

    @classmethod
    def create_new(cls, parent, json_data, user_id=None):
        try:
            instance = cls.repository.create_from_json(json_data, user_id=user_id)
            return cls.create_with_instance(parent, instance)
        except exceptions.RepositoryError as ex:
            if cls._is_unique_violation(ex):
                raise exceptions.AlreadyExist(f'Entity with {json_data} already exists in repository')
            raise

    @classmethod
    def create_with_id(cls, parent, entity_id):
        instance = cls.repository.get(entity_id)
        return cls.create_with_instance(parent, instance)

    @classmethod
    def create_with_instance(cls, parent, instance):
        if instance is None:
            raise exceptions.NotExist('Tried to create value entity with instance None. Check the call stack.')
        return cls(parent, instance)

    def __init__(self, parent, instance=None):
        super(ValueEntity, self).__init__(instance)
        self.parent = parent
