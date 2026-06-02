#  -*- coding: utf-8 -*-

import os
from importlib import import_module

from dotenv import load_dotenv

from base_api import exceptions


class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    ENVIRONMENT = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_RESPONSE_LOGGING = False
    APM_ENABLED = False

    def __init__(self):
        if self.ENVIRONMENT is None:
            raise TypeError('Use one of the specialized config classes.')
        self.SECRET_KEY = os.environ['SECRET_KEY']
        self.API_TOKEN = os.environ['API_TOKEN']
        self.API_TOKEN_HEADER = os.environ['API_TOKEN_HEADER']
        self.COOKIE_TOKEN = os.environ.get('COOKIE_TOKEN')
        self.COOKIE_USER = os.environ.get('COOKIE_USER')
        self.COOKIE_DOMAIN = os.environ.get('COOKIE_DOMAIN')
        # BASE_API_OPTIONAL: postgresql
        self.SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
        # BASE_API_OPTIONAL: celery
        self.REDIS_URL = os.environ.get('REDIS_URL')
        # BASE_API_OPTIONAL: aws
        self.CLOUD_REGION = os.environ.get('CLOUD_REGION')
        self.SNS_PLATFORM_APPLICATION_ARN = os.environ.get('SNS_PLATFORM_APPLICATION_ARN')
        self.ELASTIC_APM = {
            'SERVICE_NAME': os.environ.get('APM_SERVICE_NAME', 'base-api'),
            'SECRET_TOKEN': os.environ.get('APM_SECRET_TOKEN'),
            'SERVER_URL': os.environ.get('APM_SERVER_URL'),
            'ENVIRONMENT': self.ENVIRONMENT,
            'DEBUG': self.DEBUG,
            'CAPTURE_BODY': 'errors',
        }
        apm_enabled = os.environ.get('APM_ENABLED')
        if apm_enabled is not None:
            self.APM_ENABLED = apm_enabled.lower() in ['1', 'true', 'yes', 'on']
        api_response_logging = os.environ.get('API_RESPONSE_LOGGING')
        if api_response_logging is not None:
            self.API_RESPONSE_LOGGING = api_response_logging.lower() in ['1', 'true', 'yes', 'on']
            return
        self.API_RESPONSE_LOGGING = self.DEVELOPMENT or self.TESTING


class ProductionConfig(Config):
    ENVIRONMENT = 'production'


class StagingConfig(Config):
    ENVIRONMENT = 'staging'


class DevelopmentConfig(Config):
    ENVIRONMENT = 'development'
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ECHO = False


class SandboxConfig(Config):
    ENVIRONMENT = 'sandbox'
    DEBUG = True
    SQLALCHEMY_RECORD_QUERIES = True


class TestingConfig(DevelopmentConfig):
    ENVIRONMENT = 'test'
    TESTING = True


def get_config():
    development_config = 'base_api.infrastructure.config.DevelopmentConfig'
    app_settings = os.environ.get('APP_SETTINGS', development_config)
    if app_settings == development_config:
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        env_path = os.path.join(root_path, '.env')
        sample_env_path = os.path.join(root_path, '.env.sample')
        if os.path.exists(env_path):
            load_dotenv(verbose=True, dotenv_path=env_path)
        if not os.path.exists(env_path) and os.path.exists(sample_env_path):
            load_dotenv(verbose=True, dotenv_path=sample_env_path)

    config_imports = app_settings.split('.')
    config_class_name = config_imports[-1]
    config_module = import_module('.'.join(config_imports[:-1]))
    config_class = getattr(config_module, config_class_name, None)
    if not config_class:
        raise exceptions.ConfigClassNotFound(f'Unable to find a config class in {app_settings}')
    return config_class()
