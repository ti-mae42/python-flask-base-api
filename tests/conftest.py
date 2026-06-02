# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv

os.environ.setdefault('APP_SETTINGS', 'base_api.infrastructure.config.TestingConfig')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('API_TOKEN', 'test-api-token')
os.environ.setdefault('API_TOKEN_HEADER', 'API-TOKEN')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/1')
os.environ.setdefault('APM_ENABLED', 'False')

_env_test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env.test'))
if os.path.exists(_env_test_path):
    load_dotenv(_env_test_path, override=True)

import pytest  # noqa: E402

from base_api.initialize import web_app  # noqa: E402
from base_api.infrastructure.database import orm  # noqa: E402


@pytest.fixture(scope='session')
def app():
    assert web_app.config['TESTING'] is True, 'App is not in TESTING mode; refusing to run'
    # BASE_API_OPTIONAL: postgresql
    with web_app.app_context():
        orm.drop_all()
        orm.create_all()
    yield web_app
    with web_app.app_context():
        orm.session.remove()
        orm.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
