# -*- coding: utf-8 -*-

from flask import g

from base_api.api import resources


class DemoEntity(object):
    @classmethod
    def create(cls):
        return {'created': True}

    @classmethod
    def create_with_logged(cls, logged_user):
        return {'logged_user': logged_user}


class DemoResource(resources.ResourceBase):
    entity = DemoEntity


def test_resource_base_without_entity_initializes_me_as_none(app):
    with app.test_request_context('/'):
        resource = resources.ResourceBase()

    assert resource.me is None


def test_resource_base_creates_entity_without_logged_user(app):
    with app.test_request_context('/'):
        resource = DemoResource()

    assert resource.me == {'created': True}


def test_resource_base_creates_entity_with_logged_user(app):
    with app.test_request_context('/'):
        g.user = 'user-id'
        resource = DemoResource()

    assert resource.me == {'logged_user': 'user-id'}
