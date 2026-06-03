# -*- coding: utf-8 -*-

import pytest

from base_api import domain
from base_api.domain import services


class DemoService(services.Service):
    _domain = 'base_api.domain'


def test_service_domain_imports_configured_domain_module():
    assert DemoService.domain is domain


def test_service_domain_requires_configured_domain_module():
    with pytest.raises(NotImplementedError):
        services.Service.domain
