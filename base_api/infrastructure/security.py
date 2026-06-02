# -*- coding: utf-8 -*-

import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from passlib.apps import custom_app_context


def authenticate_api(token, expected_token):
    if token is None:
        return False
    return secrets.compare_digest(token, expected_token)


class SecurityPersonal(object):
    @staticmethod
    def hash_password(clear_password):
        return custom_app_context.hash(clear_password)

    @staticmethod
    def verify_password(clear_password, password_hash):
        return custom_app_context.verify(clear_password, password_hash)

    @staticmethod
    def generate_auth_token(subject_id, secret_key, expiration=15):
        return jwt.encode(
            {'id': subject_id, 'exp': datetime.now(UTC) + timedelta(days=expiration)},
            secret_key,
            algorithm='HS256',
        )

    @staticmethod
    def decode_token_without_verification(token):
        return jwt.decode(token, options={'verify_signature': False})

    @staticmethod
    def decode_auth_token(token, secret_key):
        return jwt.decode(token, secret_key, algorithms=['HS256'])

    @staticmethod
    def generate_recovery_code():
        return f'{secrets.randbelow(1000000):06d}'

    @staticmethod
    def generate_secret_key():
        return str(uuid.uuid4())

    @staticmethod
    def get_recovery_expiration(expiration=15):
        return datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=expiration)
