# -*- coding: utf-8 -*-

import re

from flask import g, request
from flask_restful import Resource
from pydantic import ValidationError

from base_api.api import schemas
from base_api.infrastructure import apm


class ResourceBase(Resource):
    schema: schemas.SchemaBase = None
    create_validator = None
    update_validator = None

    def __init__(self):
        self.__payload = None
        self.__valid_payload = None

    @staticmethod
    def camel_to_snake(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def snake_to_camel(name):
        result = []
        for index, part in enumerate(name.split('_')):
            if index == 0:
                result.append(part.lower())
                continue
            result.append(part.capitalize())
        return ''.join(result)

    def transform_key(self, data, method):
        if isinstance(data, dict):
            return {method(key): self.transform_key(value, method) for key, value in data.items()}
        if isinstance(data, list):
            return [self.transform_key(item, method) for item in data]
        return data

    @property
    def payload(self):
        if self.__payload is not None:
            return self.__payload
        payload = {}
        if request.is_json and request.json:
            payload.update(self.transform_key(request.json, self.camel_to_snake))
        if request.form:
            payload.update(self.transform_key(request.form, self.camel_to_snake))
        if request.args:
            payload.update(self.transform_key(request.args, self.camel_to_snake))
        if request.files:
            payload['attachment'] = request.files
        self.__payload = payload
        return self.__payload

    @property
    def headers(self):
        return request.headers

    @property
    def logged_user(self):
        return g.get('user')

    def forbidden(self):
        return self.response({'result': 'Forbidden'}, status_code=403)

    def not_allowed(self):
        return self.response({'result': 'Method not allowed'}, status_code=405)

    def unexpected_error(self, ex):
        apm.monitor.capture_exception(exc_info=True)
        return self.response({'result': 'error', 'exception': str(ex)}, status_code=500)

    def conflict(self, message):
        return self.response({'result': message}, status_code=409)

    def not_found(self, message):
        return self.response({'result': message}, status_code=404)

    def bad_request(self, message, exception=None):
        payload = {'result': message}
        if exception is not None:
            payload['exception'] = str(exception)
        apm.monitor.capture_exception(exc_info=True)
        return self.response(payload, status_code=400)

    @property
    def validator(self):
        if request.method == 'POST':
            return self.create_validator
        if request.method == 'PUT':
            return self.update_validator
        return None

    @property
    def valid_payload(self):
        valid_payload = self.__get_valid_payload()
        if request.method != 'PUT':
            return valid_payload
        return {key: value for key, value in valid_payload.items() if value is not None}

    def __get_valid_payload(self):
        if self.__valid_payload is not None:
            return self.__valid_payload
        if self.validator is None:
            self.__valid_payload = dict(self.payload)
            return self.__valid_payload
        self.__valid_payload = self.validator(**self.payload).model_dump()
        return self.__valid_payload

    def bad_request_from_validation_error(self, validation_error: ValidationError):
        errors = []
        for error in validation_error.errors():
            field_path = '.'.join(str(part) for part in error.get('loc', ()))
            if field_path:
                errors.append(f'{field_path}: {error.get("msg")}')
                continue
            errors.append(error.get('msg'))
        return self.bad_request('Invalid Request Data', '; '.join(errors))

    def no_content(self):
        return self.response({}, status_code=204)

    def response(self, result, status_code=200, compact=False):
        if self.schema is None:
            return self.transform_key(result, self.snake_to_camel), status_code

        response_schema = self.schema.create(compact=compact)
        if isinstance(result, dict):
            return self.transform_key(result, self.snake_to_camel), status_code
        if isinstance(result, list):
            payload = response_schema.dump_many(result)
            return self.transform_key(payload, self.snake_to_camel), status_code

        payload = response_schema.dump(result)
        return self.transform_key(payload, self.snake_to_camel), status_code


class HealthCheckResource(Resource):
    def get(self):
        return {'result': 'OK'}, 200
