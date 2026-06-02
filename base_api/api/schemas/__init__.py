# -*- coding: utf-8 -*-

import datetime
import decimal
import enum
import uuid


MISSING = object()


class SchemaBase(object):
    compact_fields = {'default': []}
    full_fields = {'default': []}

    @classmethod
    def create(cls, compact=False, audience='default'):
        return cls(compact, audience)

    def __init__(self, compact=False, audience='default'):
        self.compact = compact
        self.audience = audience

    @property
    def fields(self):
        if self.compact:
            return self.compact_fields[self.audience]
        return self.full_fields[self.audience]

    @staticmethod
    def read_field(source, field_name, default=MISSING):
        if isinstance(source, dict):
            return source.get(field_name, default)
        return getattr(source, field_name, default)

    def serialize_value(self, value):
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        if isinstance(value, datetime.date):
            return value.isoformat()
        if isinstance(value, decimal.Decimal):
            return float(value)
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, enum.Enum):
            return value.value
        if isinstance(value, set):
            return [self.serialize_value(item) for item in sorted(value, key=lambda item: str(item))]
        if isinstance(value, tuple):
            return [self.serialize_value(item) for item in value]
        if isinstance(value, list):
            return [self.serialize_value(item) for item in value]
        if isinstance(value, dict):
            return {key: self.serialize_value(item) for key, item in value.items()}
        return value

    def serialize_field(self, field_name, value):
        serializer = getattr(self, f'serialize_{field_name}', None)
        if serializer is None:
            return self.serialize_value(value)
        return serializer(value)

    def dump(self, source):
        dumped = {}
        for field in self.fields:
            value = self.read_field(source, field)
            if value is MISSING:
                continue
            dumped[field] = self.serialize_field(field, value)
        return dumped

    def dump_many(self, sources):
        return [self.dump(source) for source in sources]
