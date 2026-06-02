# -*- coding: utf-8 -*-

# BASE_API_OPTIONAL: aws

import boto3

from base_api import exceptions


class CloudClient(object):
    client_type = None

    def __init__(self, cloud_region=None, testing=False):
        if self.client_type is None:
            raise exceptions.CloudInvalidClientType('Use a specific cloud client implementation.')
        self.cloud_region = cloud_region
        self._client = None
        if testing:
            return
        self._client = boto3.client(self.client_type, region_name=self.cloud_region)


class SnsClient(CloudClient):
    client_type = 'sns'

    def publish(self, **kwargs):
        return self._client.publish(**kwargs)
