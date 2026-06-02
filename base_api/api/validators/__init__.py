# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict


class ValidatorBase(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
    )

    @staticmethod
    def _require_text(value, field_name):
        if not value:
            raise ValueError(f'{field_name} is required')
        return value

    @classmethod
    def _optional_text_fields(cls, value, field_name):
        if value is None:
            return value
        return cls._require_text(value, field_name)
