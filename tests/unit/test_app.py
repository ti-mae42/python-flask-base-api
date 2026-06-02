# -*- coding: utf-8 -*-

from base_api.initialize import create_app
from base_api.infrastructure import database


def test_create_app_registers_empty_api_shell(app):
    assert app.config['TESTING'] is True
    # BASE_API_OPTIONAL: postgresql
    assert database.orm is not None


def test_create_app_factory_can_build_another_app(app):
    other_app = create_app(app.config)
    assert other_app.config['TESTING'] is True
    assert any(str(rule) == '/api/healthcheck' for rule in other_app.url_map.iter_rules())
