# -*- coding: utf-8 -*-

from base_api.infrastructure import security


def test_authenticate_api_with_matching_token():
    assert security.authenticate_api('secret', 'secret') is True


def test_authenticate_api_rejects_missing_token():
    assert security.authenticate_api(None, 'secret') is False


def test_password_hash_roundtrip():
    password_hash = security.SecurityPersonal.hash_password('Strong123@')
    assert security.SecurityPersonal.verify_password('Strong123@', password_hash) is True
