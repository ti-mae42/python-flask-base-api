# -*- coding: utf-8 -*-

import requests


class Connection(object):
    headers = {}
    host = None
    url = None

    @classmethod
    def create_a_connection(cls):
        return cls()

    def __init__(self):
        self.response = None

    def get(self):
        self.response = requests.get(f'{self.host}/{self.url}', headers=self.headers, timeout=30)
        return self

    @property
    def log_data(self):
        if self.response is None:
            return {}
        return {
            'url': self.url,
            'status': self.response.status_code,
            'content': self.response.content,
        }

    @property
    def connection_error(self):
        return self.response is None

    @property
    def success(self):
        return self.response is not None and self.response.status_code in [200, 201]

    @property
    def not_found(self):
        return self.response is not None and self.response.status_code == 404

    @property
    def bad_request(self):
        return self.response is not None and self.response.status_code == 400

    @property
    def result(self):
        return self.response.json()

    @property
    def content(self):
        return self.response.content
