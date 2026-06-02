# -*- coding: utf-8 -*-

# BASE_API_OPTIONAL: database

import datetime

from sqlalchemy import desc, exc, func, select
from sqlalchemy.orm import declared_attr

from base_api import classproperty, exceptions
from base_api.infrastructure.database import orm


def _utcnow():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


class AbstractModel(object):
    query = None
    _order_by = None

    @classmethod
    def create_from_json(cls, json_data, user_id=None):
        try:
            instance = cls()
            instance.set_values(json_data)
            instance.save_db(user_id=user_id)
            return instance
        except exc.IntegrityError as ex:
            cls.rollback_db()
            raise exceptions.RepositoryError(ex)

    @classmethod
    def order_by(cls):
        if cls._order_by:
            return cls._order_by
        return [desc(cls.id)]

    @classproperty
    def select(cls):
        return select(cls)

    @classmethod
    def execute(cls, statement):
        return orm.session.execute(statement)

    @classmethod
    def list_with_filter(cls, **kwargs):
        statement = cls.select.filter_by(**kwargs).order_by(*cls.order_by())
        return cls.execute(statement).unique().scalars().all()

    @classmethod
    def count_with_filter(cls, **kwargs):
        statement = select(func.count()).select_from(cls).filter_by(**kwargs)
        return cls.execute(statement).scalar_one()

    @classmethod
    def list_with_filter_and_paginate(cls, page, page_size, **kwargs):
        statement = cls.select.filter_by(**kwargs)
        count_statement = select(func.count()).select_from(statement.subquery())
        total = cls.execute(count_statement).scalar_one()
        items_statement = statement.order_by(*cls.order_by()).offset((page - 1) * page_size).limit(page_size)
        items = cls.execute(items_statement).unique().scalars().all()
        return items, total

    @classmethod
    def list_all(cls):
        statement = cls.select.order_by(*cls.order_by())
        return cls.execute(statement).unique().scalars().all()

    @classmethod
    def get_with_filter(cls, **kwargs):
        statement = cls.select.filter_by(**kwargs)
        return cls.execute(statement).unique().scalars().one_or_none()

    @classmethod
    def get(cls, item_id):
        item = orm.session.get(cls, item_id)
        if not item:
            raise exceptions.NotExist
        return item

    @classmethod
    def rollback_db(cls):
        orm.session.rollback()

    def save_db(self, user_id=None):
        self._set_audit_user(user_id)
        orm.session.add(self)
        orm.session.flush()
        orm.session.refresh(self)

    def delete_db(self, user_id=None):
        try:
            orm.session.delete(self)
            orm.session.flush()
        except exc.IntegrityError as ex:
            raise exceptions.RepositoryError(ex)

    def update_from_json(self, json_data, user_id=None):
        try:
            self.set_values(json_data)
            self.save_db(user_id=user_id)
            return self
        except exc.IntegrityError as ex:
            raise exceptions.RepositoryError(ex)

    def set_values(self, json_data):
        for key, value in json_data.items():
            setattr(self, key, value)

    def _set_audit_user(self, user_id):
        if user_id is None:
            return
        if hasattr(self, 'updated_by_id'):
            self.updated_by_id = user_id
        if hasattr(self, 'created_by_id') and getattr(self, 'id', None) is None:
            self.created_by_id = user_id


class AuditMixin(object):
    @declared_attr
    def created_at(cls):
        return orm.Column(orm.DateTime, server_default=func.now(), default=_utcnow)

    @declared_attr
    def updated_at(cls):
        return orm.Column(orm.DateTime, server_default=func.now(), onupdate=_utcnow, default=_utcnow)
