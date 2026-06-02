# -*- coding: utf-8 -*-

from functools import wraps

from flask import Response, g
from flask_restful import Api


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('authenticated', False):
            return Response('{"result": "Not Authorized"}', 401, content_type='application/json')
        return f(*args, **kwargs)

    return decorated_function


def not_allowed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return Response('{"result": "Method not allowed"}', 405, content_type='application/json')

    return decorated_function


def create_api(app):
    from base_api.api import resources

    api = Api(app)
    api.add_resource(resources.HealthCheckResource, '/api/healthcheck')
    return api
