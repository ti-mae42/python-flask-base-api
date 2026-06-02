# -*- coding: utf-8 -*-

import os

from elasticapm.contrib import flask as flask_apm

monitor = None


class _NoopMonitor(object):
    def capture_exception(self, *args, **kwargs):
        return None

    def capture_message(self, *args, **kwargs):
        return None


def _is_test_run(app):
    return app.config.get('TESTING', False) or 'PYTEST_CURRENT_TEST' in os.environ


def create_monitor(app):
    global monitor
    if not app.config.get('APM_ENABLED'):
        monitor = _NoopMonitor()
        return monitor
    if _is_test_run(app):
        monitor = _NoopMonitor()
        return monitor
    try:
        monitor = flask_apm.ElasticAPM(app)
    except Exception:
        monitor = _NoopMonitor()
    return monitor
