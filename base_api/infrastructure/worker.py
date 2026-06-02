# -*- coding: utf-8 -*-

# BASE_API_OPTIONAL: celery

from celery import Celery


def create_worker(app):
    broker_url = app.config.get('REDIS_URL')
    worker = Celery(app.import_name, broker=broker_url, backend=broker_url)
    worker.conf.update(app.config)
    return worker
