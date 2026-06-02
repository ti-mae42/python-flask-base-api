# -*- coding: utf-8 -*-

import pytest

from base_api.infrastructure.validation import PasswordValidator


def test_validate_strong_password():
    assert PasswordValidator.validate_strong_password('Strong123@') == 'Strong123@'


def test_validate_strong_password_rejects_weak_password():
    with pytest.raises(ValueError):
        PasswordValidator.validate_strong_password('weak')
