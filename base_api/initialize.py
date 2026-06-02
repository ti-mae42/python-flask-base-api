# -*- coding: utf-8 -*-

import json

from flask import Flask, g, request

from base_api import api, commands, config
from base_api.infrastructure import apm, database, security, worker


def create_app(config_object=None):
    app = Flask(__name__)
    if isinstance(config_object, dict):
        app.config.from_mapping(config_object)
    else:
        app.config.from_object(config_object or config)

    # BASE_API_OPTIONAL: postgresql
    database.register_orm(app)
    database.register_migration(app)
    apm.create_monitor(app)
    commands.register(app)
    api.create_api(app)
    register_request_hooks(app)

    return app


def register_request_hooks(app):
    @app.before_request
    def authenticate_request():
        token = request.headers.get(app.config['API_TOKEN_HEADER'])
        g.authenticated = security.authenticate_api(token, app.config['API_TOKEN'])
        g.user = None

    @app.after_request
    def log_api_json_response(response):
        if not app.config.get('API_RESPONSE_LOGGING'):
            return response
        if not response.is_json:
            return response
        payload = response.get_json(silent=True)
        if payload is None:
            return response
        app.logger.warning(
            'API response %s %s %s\n%s',
            request.method,
            request.full_path.rstrip('?'),
            response.status,
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
        )
        return response

    @app.after_request
    def add_cache_header(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response


web_app = create_app()

# BASE_API_OPTIONAL: celery
celery_app = worker.create_worker(web_app)
