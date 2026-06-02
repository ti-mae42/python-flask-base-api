# -*- coding: utf-8 -*-

import re


class PasswordValidator(object):
    _error_message = (
        'password must be at least 8 characters long and include uppercase, lowercase, number, and special character'
    )

    @classmethod
    def validate_strong_password(cls, password):
        normalized_password = str(password or '')
        if len(normalized_password) < 8:
            raise ValueError(cls._error_message)
        if not re.search(r'[A-Z]', normalized_password):
            raise ValueError(cls._error_message)
        if not re.search(r'[a-z]', normalized_password):
            raise ValueError(cls._error_message)
        if not re.search(r'\d', normalized_password):
            raise ValueError(cls._error_message)
        if not re.search(r'[^A-Za-z0-9]', normalized_password):
            raise ValueError(cls._error_message)
        return normalized_password
